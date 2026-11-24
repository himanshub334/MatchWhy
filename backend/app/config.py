from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    database_url:str="sqlite:///./matchwhy.db"
    jobsense_api_url:str=""
    openai_api_key:str=""
    openai_base_url:str="https://api.openai.com/v1"
    llm_model:str="gpt-4o-mini"
settings=Settings()
