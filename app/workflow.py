import logging
import re
from typing import List, Optional
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from app.sql_generation import get_sql_gen_chain

# Set up module logger
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)

class GraphState(TypedDict):
    error: str  # Tracks if an error has occurred
    messages: List  # List of messages (user input and assistant messages)
    generation: Optional[dict]  # Holds the generated SQL query (structured output)
    iterations: int  # Keeps track of how many times the workflow has retried
    results: Optional[List]  # Holds the results of SQL execution
    no_records_found: bool  # Flag for whether any records were found in the SQL result
    translated_input: str  # Holds the translated user input
    database_schema: str  # Holds the extracted database schema for context checking

def get_workflow(conn, cursor, vector_store):
    """Define and compile the LangGraph workflow."""
    # Max iterations: defines how many times the workflow should retry in case of errors
    max_iterations = 3
    # SQL generation chain: this is a chain that will generate SQL based on retrieved docs
    sql_gen_chain = get_sql_gen_chain()
    # Initialize OpenAI LLM for translation and safety checks
    llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")

    # --- Define node functions (they close over conn, cursor, vector_store, sql_gen_chain, llm, max_iterations) ---

    def translate_input(state: GraphState) -> GraphState:
        """Translate user input to English (or repeat if already English)."""
        _logger.info("Starting translation of user input to English.")
        messages = state["messages"]
        user_input = messages[-1][1]  # Get the latest user input
        translation_prompt = f"""
        Translate the following text to English. If the text is already in English, repeat it exactly without any additional explanation.
        Text:
        {user_input}
        """
        translated_response = llm.invoke(translation_prompt)
        translated_text = getattr(translated_response, "content", "").strip()
        state["translated_input"] = translated_text
        _logger.info("Translation completed successfully. Translated input: %s", translated_text)
        return state

    def pre_safety_check(state: GraphState) -> GraphState:
        """Perform safety checks on the user input."""
        _logger.info("Performing safety check.")
        translated_input = state.get("translated_input", "")
        messages = state.get("messages", [])
        error = "no"
        disallowed_operations = ['CREATE', 'DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
        pattern = re.compile(r'\b(' + '|'.join(disallowed_operations) + r')\b', re.IGNORECASE)
        if pattern.search(translated_input):
            _logger.warning("Input contains disallowed SQL operations. Halting the workflow.")
            error = "yes"
            messages += [("assistant", "Your query contains disallowed SQL operations and cannot be processed.")]
        else:
            # Use LLM to check for toxic/inappropriate content
            safety_prompt = f"""
            Analyze the following input for any toxic or inappropriate content.
            Respond with only "safe" or "unsafe", and nothing else.
            Input:
            {translated_input}
            """
            safety_invoke = llm.invoke(safety_prompt)
            safety_response = getattr(safety_invoke, "content", "").strip().lower()
            if safety_response == "safe":
                _logger.info("Input is safe to process.")
            else:
                _logger.warning("Input contains inappropriate content. Halting the workflow.")
                error = "yes"
                messages += [("assistant", "Your query contains inappropriate content and cannot be processed.")]
        state["error"] = error
        state["messages"] = messages
        return state

    def schema_extract(state: GraphState) -> GraphState:
        """Extract database schema (tables and columns)."""
        _logger.info("Extracting database schema.")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema_details = []
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_defs = ', '.join([f"{col[1]} ({col[2]})" for col in columns])
            schema_details.append(f"- {table_name}({column_defs})")
        database_schema = '\n'.join(schema_details)
        state["database_schema"] = database_schema
        _logger.info("Database schema extracted:\n%s", database_schema)
        return state

    def context_check(state: GraphState) -> GraphState:
        """Check whether the user's input is relevant to the extracted schema."""
        _logger.info("Performing context check.")
        translated_input = state.get("translated_input", "")
        messages = state.get("messages", [])
        error = "no"
        database_schema = state.get("database_schema", "")
        context_prompt = f"""
        Determine whether the following user input is a question that can be answered using the database schema provided below.
        Respond with only "relevant" if the input is relevant to the database schema, or "irrelevant" if it is not.
        User Input:
        {translated_input}
        Database Schema:
        {database_schema}
        """
        llm_invoke = llm.invoke(context_prompt)
        llm_response = getattr(llm_invoke, "content", "").strip().lower()
        if llm_response == "relevant":
            _logger.info("Input is relevant to the database schema.")
        else:
            _logger.info("Input is not relevant. Halting the workflow.")
            error = "yes"
            messages += [("assistant", "Your question is not related to the database and cannot be processed.")]
        state["error"] = error
        state["messages"] = messages
        return state

    def generate(state: GraphState) -> GraphState:
        """Generate an SQL query using the SQL generation chain and vector store."""
        _logger.info("Generating SQL query.")
        messages = state.get("messages", [])
        iterations = state.get("iterations", 0)
        translated_input = state.get("translated_input", "")
        database_schema = state.get("database_schema", "")
        # Retrieve relevant docs from vector store
        docs = vector_store.similarity_search(translated_input, k=4)
        retrieved_docs = "\n\n".join([getattr(doc, "page_content", str(doc)) for doc in docs])
        # Generate the SQL query using the SQL generation chain
        sql_solution = sql_gen_chain.invoke({
            "retrieved_docs": retrieved_docs,
            "database_schema": database_schema,
            "messages": [("user", translated_input)],
        })
        # Append assistant message with solution
        description = getattr(sql_solution, "description", "")
        sql_code = getattr(sql_solution, "sql_code", "")
        messages += [("assistant", f"{description}\nSQL Query:\n{sql_code}")]
        iterations += 1
        _logger.info("Generated SQL query:\n%s", sql_code)
        state["generation"] = sql_solution
        state["messages"] = messages
        state["iterations"] = iterations
        return state

    def post_safety_check(state: GraphState) -> GraphState:
        """Check generated SQL for disallowed operations."""
        _logger.info("Performing post-safety check on the generated SQL query.")
        sql_solution = state.get("generation", {})
        sql_query = getattr(sql_solution, "sql_code", "")
        messages = state.get("messages", [])
        error = "no"
        disallowed_operations = ['CREATE', 'DELETE', 'DROP', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE']
        pattern = re.compile(r'\b(' + '|'.join(disallowed_operations) + r')\b', re.IGNORECASE)
        found_operations = pattern.findall(sql_query)
        if found_operations:
            _logger.warning("Generated SQL query contains disallowed SQL operations: %s. Halting the workflow.", ", ".join(set(found_operations)))
            error = "yes"
            messages += [("assistant", f"The generated SQL query contains disallowed SQL operations: {', '.join(set(found_operations))} and cannot be processed.")]
        else:
            _logger.info("Generated SQL query passed the safety check.")
        state["error"] = error
        state["messages"] = messages
        return state

    def sql_check(state: GraphState) -> GraphState:
        """Validate the SQL by attempting execution inside a savepoint and rolling back."""
        _logger.info("Validating SQL query.")
        messages = state.get("messages", [])
        sql_solution = state.get("generation", {})
        error = "no"
        sql_code = getattr(sql_solution, "sql_code", "").strip()
        try:
            conn.execute('SAVEPOINT sql_check;')
            cursor.execute(sql_code)
            conn.execute('ROLLBACK TO sql_check;')
            _logger.info("SQL query validation: success.")
        except Exception as e:
            conn.execute('ROLLBACK TO sql_check;')
            _logger.error("SQL query validation failed. Error: %s", e)
            messages += [("user", f"Your SQL query failed to execute: {e}")]
            error = "yes"
        state["error"] = error
        state["messages"] = messages
        return state

    def run_query(state: GraphState) -> GraphState:
        """Execute the SQL (commit changes for non-SELECT or return rows for SELECT)."""
        _logger.info("Running SQL query.")
        sql_solution = state.get("generation", {})
        sql_code = getattr(sql_solution, "sql_code", "").strip()
        results = None
        no_records_found = False
        generated_answer = None
        try:
            cursor.execute(sql_code)
            if sql_code.upper().startswith("SELECT"):
                results = cursor.fetchall()
                if not results:
                    no_records_found = True
                    generated_answer = "No records found for your query."
                    _logger.info("SQL query execution: success. No records found.")
                else:
                    # Génère une phrase-réponse à partir des résultats
                    # Ex : "There are X users in the database." ou "The result is ..."
                    if len(results) == 1 and len(results[0]) == 1:
                        generated_answer = f"The answer is: {results[0][0]}"
                    else:
                        generated_answer = f"The result is: {results}"
                    _logger.info("SQL query execution: success.")
            else:
                conn.commit()
                generated_answer = "Query executed successfully. Changes committed."
                _logger.info("SQL query execution: success. Changes committed.")
        except Exception as e:
            generated_answer = f"Error executing SQL query: {e}"
            _logger.error("SQL query execution failed. Error: %s", e)
        state["results"] = results
        state["no_records_found"] = no_records_found
        state["generated_answer"] = generated_answer
        return state

    def decide_next_step(state: GraphState) -> str:
        """Decide whether to run query, retry generation, or end the workflow."""
        _logger.info("Deciding next step based on current state.")
        error = state.get("error", "")
        iterations = state.get("iterations", 0)
        if error == "no":
            _logger.info("Error status: no. Proceeding with running the query.")
            return "run_query"
        elif iterations >= max_iterations:
            _logger.info("Maximum iterations reached. Ending the workflow.")
            return END
        else:
            _logger.info("Error detected. Retrying SQL query generation.")
            return "generate"

    def translate_answer(state: GraphState) -> GraphState:
        """Translate the generated answer to the language of the user's question."""
        _logger.info("Translating generated answer to user's language.")
        generated_answer = state.get("generated_answer", "")
        # Détecte la langue de la question originale
        user_input = state["messages"][0][1]
        # Utilise l'API OpenAI pour traduire la réponse dans la langue de la question
        prompt = f"Translate the following answer to the language of this question.\nQuestion: {user_input}\nAnswer: {generated_answer}"
        translation = llm.invoke(prompt)
        translated = getattr(translation, "content", "").strip()
        state["generated_answer"] = translated
        return state
    workflow = StateGraph(GraphState)
    workflow.add_node("translate_input", translate_input)
    workflow.add_node("pre_safety_check", pre_safety_check)
    workflow.add_node("schema_extract", schema_extract)
    workflow.add_node("context_check", context_check)
    workflow.add_node("generate", generate)
    workflow.add_node("post_safety_check", post_safety_check)
    workflow.add_node("sql_check", sql_check)
    workflow.add_node("run_query", run_query)
    workflow.add_node("translate_answer", translate_answer)

    workflow.add_edge(START, "translate_input")
    workflow.add_edge("translate_input", "pre_safety_check")
    workflow.add_conditional_edges(
        "pre_safety_check",
        lambda state: "schema_extract" if state["error"] == "no" else END,
        {"schema_extract": "schema_extract", END: END},
    )
    workflow.add_edge("schema_extract", "context_check")
    workflow.add_conditional_edges(
        "context_check",
        lambda state: "generate" if state["error"] == "no" else END,
        {"generate": "generate", END: END},
    )
    workflow.add_edge("generate", "post_safety_check")
    workflow.add_conditional_edges(
        "post_safety_check",
        lambda state: "sql_check" if state["error"] == "no" else END,
        {"sql_check": "sql_check", END: END},
    )
    workflow.add_conditional_edges(
        "sql_check",
        decide_next_step,
        {
            "run_query": "run_query",
            "generate": "generate",
            END: END
        }
    )
    workflow.add_edge("run_query", "translate_answer")
    workflow.add_edge("translate_answer", END)

    app = workflow.compile()
    return app
