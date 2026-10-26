from django.shortcuts import render
from django.db import connection
import logging
from .services import get_sql_from_llm, summarize_results
from .config import Config


logger = logging.getLogger(__name__)

def home(request):
    # 1. Get the raw model name (e.g., "qwen/qwen3 coder...")
    raw_model = Config.GROQ_MODEL
    
    # 2. Clean it up for display (Optional: removes 'qwen/' prefix if present)
    display_model = raw_model.split('/')[-1] if '/' in raw_model else raw_model

    return render(request, 'home.html', {
        'model_name': display_model
    })

def dashboard(request):
    results = None
    columns = None
    sql_query = None
    error = None
    summary = None
    user_question = ""

    # --- THE FIX IS HERE ---
    # Check if the question came from Dashboard (POST) OR Home Page (GET)
    if request.method == 'POST':
        user_question = request.POST.get('question', '')
    elif request.method == 'GET':
        user_question = request.GET.get('question', '')
    # -----------------------

    if user_question:
        # 1. Get SQL from LLM
        generated_sql = get_sql_from_llm(user_question)
        
        # 2. Check for LLM Errors (e.g., "I cannot answer...")
        if generated_sql.startswith("ERROR") or generated_sql.startswith("Error"):
            error = generated_sql
        else:
            sql_query = generated_sql
            try:
                # 3. Run Query
                with connection.cursor() as cursor:
                    cursor.execute(sql_query)
                    if cursor.description:
                        columns = [col[0] for col in cursor.description]
                        results = cursor.fetchall()
                        
                        # 4. Summarize (Only if we have results)
                        if results:
                            summary = summarize_results(user_question, results, columns)
                            
            except Exception as e:
                error = f"Database Error: {str(e)}"
                logger.error(error)
    print("🔥 DASHBOARD FUNCTION CALLED 🔥")
    return render(request, 'dashboard.html', {
        'results': results,
        'columns': columns,
        'sql_query': sql_query,
        'error': error,
        'summary': summary, 
        'user_question': user_question
    })
    