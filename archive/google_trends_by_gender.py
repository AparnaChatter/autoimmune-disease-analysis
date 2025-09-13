# Script to fetch Google Trends data for gendered queries for autoimmune diseases
import yaml
# from pytrends.request import TrendReq
# import time

def main():
    cfg = yaml.safe_load(open("src/config/diseases.yaml", "r", encoding="utf-8").read())
    genders = ["women", "men"]
    print("Gendered Google Trends search terms:")
    for d in cfg["diseases"]:
        for gender in genders:
            for term in d["trends_terms"]:
                gendered_term = f"{term} {gender}"
                print(gendered_term)
    print("\nPlease use these terms in Google Trends manually or automate with pytrends/selenium as needed.")

if __name__ == "__main__":
    main()
