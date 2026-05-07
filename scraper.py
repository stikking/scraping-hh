import requests
import pandas as pd
import time

def scrape_global_jobs(api_key, search_queries, results_per_query=500):
    all_vacancies = []
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    for query in search_queries:
        print(f"Собираем: {query}...")
        
        pages_needed = results_per_query // 100
        
        for page_num in range(1, pages_needed + 1):
            querystring = {
                "query": f"{query}",
                "page": str(page_num),
                "num_pages": "10" 
            }
            
            try:
                response = requests.get(url, headers=headers, params=querystring)
                if response.status_code != 200:
                    print(f" Ошибка {response.status_code}")
                    break
                    
                data = response.json()
                jobs = data.get("data", [])
                
                if not jobs:
                    break
                    
                for job in jobs:
                    posted = job.get("job_posted_at_datetime_utc", "")
                    posted_date = posted[:10] if posted else ""
                    
                    all_vacancies.append({
                        "id": job.get("job_id", ""),
                        "name": job.get("job_title", ""),
                        "employer": job.get("employer_name", ""),
                        "area": f"{job.get('job_city', '')}, {job.get('job_country', '')}",
                        "published_at": posted_date,
                        "salary_from": job.get("job_min_salary"),
                        "salary_to": job.get("job_max_salary"),
                        "currency": job.get("job_salary_currency", ""),
                        "experience": "" 
                    })
                time.sleep(0.3)
            except Exception as e:
                print(f" Ошибка: {e}")
                break
                
    return pd.DataFrame(all_vacancies)

if __name__ == "__main__":
    queries = [
        "Data Scientist", "Python Developer", "Data Engineer", 
        "Machine Learning Engineer", "DevOps Engineer", "Data Analyst", 
        "Backend Developer", "AI Researcher", "Software Engineer", "Frontend Developer"
    ]
    
    API_KEY = "e8d45a6382msh63c4dc64239eca2p1c9f48jsnd74515262ef4" 
    
    df = scrape_global_jobs(API_KEY, queries, results_per_query=500)
    
    print(f"\nСобрано всего: {len(df)}")
    
    if df.empty:
        print("ОШИБКА: Не удалось собрать данные. Проверь правильность API ключа.")
    else:
        df = df.drop_duplicates(subset=["id"])
        df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
        df = df.dropna(subset=["name"])
        
        print(f"После очистки: {len(df)}")
        
        df.to_csv("vacancies.csv", index=False, encoding="utf-8-sig")
        print("Данные успешно сохранены в vacancies.csv")