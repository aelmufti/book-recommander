"""
Adaptateur de base de données pour supporter DuckDB (local) et PostgreSQL (production)
"""
import os
import duckdb
from sqlalchemy import create_engine, text
import pandas as pd

class DatabaseAdapter:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.is_production = bool(self.database_url)
        
        if self.is_production:
            # Production: PostgreSQL
            self.engine = create_engine(self.database_url)
            self.conn_type = "postgresql"
            print("🐘 Using PostgreSQL (production)")
        else:
            # Local: DuckDB avec la base légère pour déploiement
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Essayer d'abord la base de déploiement, sinon la base complète
            deployment_db = os.path.join(script_dir, "books_deployment.duckdb")
            full_db = os.path.join(script_dir, "books.duckdb")
            
            if os.path.exists(deployment_db):
                db_path = deployment_db
                print("🦆 Using DuckDB (deployment - 56k books)")
            elif os.path.exists(full_db):
                db_path = full_db
                print("🦆 Using DuckDB (full - 43M books)")
            else:
                # Créer une base vide
                db_path = deployment_db
                print("🦆 Creating new DuckDB database")
            
            self.conn = duckdb.connect(db_path)
            self.conn_type = "duckdb"
    
    def execute_query(self, query, params=None):
        """Exécuter une requête selon le type de base"""
        if self.is_production:
            # PostgreSQL avec SQLAlchemy
            with self.engine.connect() as conn:
                result = conn.execute(text(query), params or {})
                return result.fetchall()
        else:
            # DuckDB
            if params:
                return self.conn.execute(query, params).fetchall()
            return self.conn.execute(query).fetchall()
    
    def migrate_data_if_needed(self):
        """Migrer les données vers PostgreSQL si nécessaire"""
        if not self.is_production:
            return
            
        # Vérifier si les données existent déjà
        try:
            result = self.execute_query("SELECT COUNT(*) FROM books LIMIT 1")
            if result and result[0][0] > 0:
                print("✅ Données déjà présentes en base PostgreSQL")
                return
        except:
            pass
        
        print("🔄 Migration des données vers PostgreSQL...")
        
        # Lire depuis le parquet français (plus petit)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parquet_file = os.path.join(script_dir, "books_french.parquet")
        
        if os.path.exists(parquet_file):
            df = pd.read_parquet(parquet_file)
            print(f"📊 {len(df):,} livres français à migrer")
        else:
            print("❌ Aucun fichier de données trouvé")
            return
        
        # Migrer vers PostgreSQL
        df.to_sql("books", self.engine, if_exists="replace", index=False, chunksize=1000)
        
        # Créer les index
        with self.engine.connect() as conn:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_title ON books(title)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_authors ON books(authors)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_language ON books(language)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_books_popularity ON books(popularity_tier)"))
            conn.commit()
        
        print("✅ Migration terminée avec index")
    
    def close(self):
        """Fermer la connexion"""
        if not self.is_production and hasattr(self, 'conn'):
            self.conn.close()