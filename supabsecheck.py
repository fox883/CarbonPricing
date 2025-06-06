from supabase import create_client

SUPABASE_URL = "https://ezwgzkpzbszznoqgfakv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6d2d6a3B6YnN6em5vcWdmYWt2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDkyMDcxMDIsImV4cCI6MjA2NDc4MzEwMn0.YwcQG7fye5s1dgGUGuhTwrtfVld5xVoTekvhxBOKVQ0"  # <-- now works!

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("projects").select("*").execute()
    print(response.data)
except Exception as e:
    print("Error:", str(e))