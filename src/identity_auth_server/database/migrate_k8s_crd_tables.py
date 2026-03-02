"""Database migration script for K8s CRD metadata tables.

This migration adds tables for storing Kubernetes CRD metadata to enable
proper namespace isolation, labeling, and status tracking for MultiAgentSystem
and ZTAPolicy custom resources.

Run this script after deploying the K8s CRD backend APIs.
"""

from sqlmodel import SQLModel, create_engine

from identity_auth_server.core.k8s_db_types import K8sMultiAgentSystemCRD, K8sZTAPolicyCRD


def run_migration(database_url: str):
    """Create K8s CRD metadata tables.
    
    Args:
        database_url: PostgreSQL connection string
    """
    print("Creating K8s CRD metadata tables...")
    engine = create_engine(database_url)
    
    # Create tables
    SQLModel.metadata.create_all(engine, tables=[
        K8sMultiAgentSystemCRD.__table__,
        K8sZTAPolicyCRD.__table__,
    ])
    
    print("✓ K8s CRD metadata tables created successfully")
    print("  - k8s_multiagentsystem_crd")
    print("  - k8s_ztapolicy_crd")


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Construct from individual components
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "identity_auth_server")
        db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    print(f"Database URL: {db_url}")
    run_migration(db_url)
