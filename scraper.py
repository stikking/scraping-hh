import requests
import pandas as pd
import time

def scrape_hh_jobs(search_queries, max_per_query=1000):
    all_vacancies = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Host": "api.hh.ru"
    }
    
    for query in search_queries:
        print(f"Собираем: {query}...")
        page = 0
        while True:
            url = "https://api.hh.ru/vacancies"
            params = {
                "text": query,
                "area": 113,
                "per_page": 100,
                "page": page
            }
            
            try:
                response = requests.get(url, params=params, headers=headers)
                
                if response.status_code != 200:
                    print(f" Ошибка доступа ({response.status_code}).")
                    break
                    
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    break
                    
                for item in items:
                    salary = item.get("salary") or {}
                    all_vacancies.append({
                        "id": item["id"],
                        "name": item["name"],
                        "employer": item["employer"]["name"],
                        "area": item["area"]["name"],
                        "published_at": item["published_at"],
                        "salary_from": salary.get("from"),
                        "salary_to": salary.get("to"),
                        "currency": salary.get("currency"),
                        "experience": item.get("experience", {}).get("name")
                    })
                page += 1
                time.sleep(0.2)
                
                if page * 100 >= max_per_query:
                    break
            except Exception as e:
                print(f" Ошибка: {e}")
                break

    return pd.DataFrame(all_vacancies)

if __name__ == "__main__":
    queries = [
        "Data Scientist", "Python developer", "Data Engineer", 
        "ML engineer", "DevOps", "Data Analyst", "Backend developer", "AI researcher"
    ]
    
    df = scrape_hh_jobs(queries, max_per_query=800)
    
    print(f"\nСобрано всего: {len(df)}")
    
    if df.empty:
        print("ОШИБКА: Не удалось собрать данные. IP заблокирован hh.ru.")
    else:
        df = df.drop_duplicates(subset=["id"])
        df["published_at"] = pd.to_datetime(df["published_at"]).dt.date
        df = df.dropna(subset=["name"]) # Удаляем пустые
        
        print(f"После очистки: {len(df)}")
        
        df.to_csv("vacancies.csv", index=False, encoding="utf-8-sig")
        print("Данные успешно сохранены в vacancies.csv")