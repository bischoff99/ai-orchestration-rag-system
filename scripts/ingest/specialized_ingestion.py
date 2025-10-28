#!/usr/bin/env python3
"""
Specialized Data Ingestion
Targeted ingestion for specific use cases and domains
"""

import os
import sys
import time
from datasets import load_dataset
from typing import List, Dict, Any
import json

# Add the examples directory to path
sys.path.append('/Users/andrejsp/ai/examples')

from rag_setup import RAGVectorDB

class SpecializedIngestion:
    """Specialized data ingestion for specific domains"""
    
    def __init__(self):
        self.rag_systems = {
            "ai_ml": RAGVectorDB(backend="chroma", collection_name="ai_ml_knowledge"),
            "devops": RAGVectorDB(backend="chroma", collection_name="devops_knowledge"),
            "security": RAGVectorDB(backend="chroma", collection_name="security_knowledge"),
            "data_science": RAGVectorDB(backend="chroma", collection_name="data_science_knowledge")
        }
    
    def ingest_ai_ml_datasets(self):
        """Ingest AI/ML specific datasets"""
        print("🤖 Ingesting AI/ML datasets...")
        
        # AI/ML documentation
        ai_docs = [
            {
                "title": "Deep Learning Fundamentals",
                "content": """
                Deep Learning Fundamentals
                
                Neural Networks:
                - Perceptrons: Basic building blocks
                - Multi-layer Perceptrons: Multiple layers
                - Backpropagation: Training algorithm
                - Activation Functions: ReLU, Sigmoid, Tanh
                
                Convolutional Neural Networks (CNNs):
                - Convolutional Layers: Feature extraction
                - Pooling Layers: Dimensionality reduction
                - Fully Connected Layers: Classification
                
                Recurrent Neural Networks (RNNs):
                - LSTM: Long Short-Term Memory
                - GRU: Gated Recurrent Unit
                - Attention Mechanisms: Focus on important parts
                """,
                "category": "deep_learning"
            },
            {
                "title": "Machine Learning Algorithms",
                "content": """
                Machine Learning Algorithms Overview
                
                Supervised Learning:
                - Linear Regression: Predict continuous values
                - Logistic Regression: Binary classification
                - Decision Trees: Rule-based classification
                - Random Forest: Ensemble of decision trees
                - SVM: Support Vector Machines
                - Neural Networks: Deep learning models
                
                Unsupervised Learning:
                - K-Means: Clustering algorithm
                - Hierarchical Clustering: Tree-based clustering
                - PCA: Principal Component Analysis
                - DBSCAN: Density-based clustering
                
                Reinforcement Learning:
                - Q-Learning: Value-based learning
                - Policy Gradient: Direct policy optimization
                - Actor-Critic: Combined approach
                """,
                "category": "algorithms"
            },
            {
                "title": "MLOps Best Practices",
                "content": """
                MLOps Best Practices
                
                Model Development:
                - Version Control: Git for code and data
                - Experiment Tracking: MLflow, Weights & Biases
                - Data Validation: Great Expectations
                - Feature Stores: Feast, Tecton
                
                Model Deployment:
                - Containerization: Docker for models
                - Orchestration: Kubernetes for scaling
                - API Design: RESTful ML APIs
                - A/B Testing: Model comparison
                
                Model Monitoring:
                - Data Drift: Monitor input distribution
                - Model Drift: Monitor prediction quality
                - Performance Metrics: Accuracy, latency
                - Alerting: Automated issue detection
                """,
                "category": "mlops"
            }
        ]
        
        documents = []
        metadatas = []
        
        for i, doc in enumerate(ai_docs):
            documents.append(doc["content"])
            metadatas.append({
                "source": "ai_ml_docs",
                "title": doc["title"],
                "category": doc["category"],
                "type": "ai_ml",
                "index": i,
                "collection": "ai_ml"
            })
        
        if documents:
            self.rag_systems["ai_ml"].add_documents(documents, metadatas)
            print(f"✅ Added {len(documents)} AI/ML documents")
    
    def ingest_devops_datasets(self):
        """Ingest DevOps and infrastructure datasets"""
        print("🔧 Ingesting DevOps datasets...")
        
        devops_docs = [
            {
                "title": "Kubernetes Architecture",
                "content": """
                Kubernetes Architecture Deep Dive
                
                Control Plane Components:
                - API Server: REST API for cluster management
                - etcd: Distributed key-value store for cluster state
                - Scheduler: Assigns pods to nodes
                - Controller Manager: Manages cluster controllers
                
                Node Components:
                - kubelet: Node agent managing pods
                - kube-proxy: Network proxy for services
                - Container Runtime: Docker, containerd, CRI-O
                
                Networking:
                - Pod Network: Communication between pods
                - Service Network: Stable network endpoints
                - Ingress: External access to services
                - CNI: Container Network Interface plugins
                """,
                "category": "kubernetes"
            },
            {
                "title": "CI/CD Pipeline Design",
                "content": """
                CI/CD Pipeline Design Principles
                
                Continuous Integration:
                - Source Control: Git-based workflows
                - Automated Testing: Unit, integration, e2e tests
                - Code Quality: Linting, security scanning
                - Build Automation: Compile, package, containerize
                
                Continuous Deployment:
                - Environment Promotion: Dev → Staging → Prod
                - Blue-Green Deployment: Zero-downtime updates
                - Canary Releases: Gradual rollout
                - Rollback Strategies: Quick recovery
                
                Tools and Platforms:
                - Jenkins: Open-source automation server
                - GitLab CI: Integrated CI/CD platform
                - GitHub Actions: Cloud-based workflows
                - ArgoCD: GitOps continuous delivery
                """,
                "category": "cicd"
            },
            {
                "title": "Infrastructure as Code",
                "content": """
                Infrastructure as Code (IaC) Best Practices
                
                Terraform:
                - Declarative Configuration: Define desired state
                - State Management: Track infrastructure changes
                - Modules: Reusable infrastructure components
                - Providers: Cloud and service integrations
                
                Ansible:
                - Agentless Automation: SSH-based management
                - Playbooks: YAML-based automation
                - Roles: Reusable automation units
                - Inventory: Host and group management
                
                CloudFormation:
                - AWS Native: Integrated with AWS services
                - Templates: JSON/YAML infrastructure definitions
                - Stacks: Logical grouping of resources
                - Drift Detection: Monitor configuration changes
                """,
                "category": "iac"
            }
        ]
        
        documents = []
        metadatas = []
        
        for i, doc in enumerate(devops_docs):
            documents.append(doc["content"])
            metadatas.append({
                "source": "devops_docs",
                "title": doc["title"],
                "category": doc["category"],
                "type": "devops",
                "index": i,
                "collection": "devops"
            })
        
        if documents:
            self.rag_systems["devops"].add_documents(documents, metadatas)
            print(f"✅ Added {len(documents)} DevOps documents")
    
    def ingest_security_datasets(self):
        """Ingest cybersecurity and security datasets"""
        print("🔒 Ingesting Security datasets...")
        
        security_docs = [
            {
                "title": "OWASP Top 10 Security Risks",
                "content": """
                OWASP Top 10 Security Risks (2021)
                
                1. Broken Access Control: Improper access restrictions
                2. Cryptographic Failures: Weak encryption implementation
                3. Injection: SQL, NoSQL, LDAP injection attacks
                4. Insecure Design: Flawed security architecture
                5. Security Misconfiguration: Default/incomplete configurations
                6. Vulnerable Components: Outdated libraries/frameworks
                7. Authentication Failures: Weak authentication mechanisms
                8. Software Integrity Failures: Supply chain attacks
                9. Logging Failures: Insufficient security monitoring
                10. Server-Side Request Forgery: SSRF attacks
                """,
                "category": "owasp"
            },
            {
                "title": "Zero Trust Security Model",
                "content": """
                Zero Trust Security Architecture
                
                Core Principles:
                - Never Trust, Always Verify: Continuous authentication
                - Least Privilege Access: Minimal required permissions
                - Assume Breach: Design for compromise scenarios
                
                Implementation:
                - Identity Verification: Multi-factor authentication
                - Device Trust: Device compliance checking
                - Network Segmentation: Micro-segmentation
                - Data Protection: Encryption at rest and in transit
                - Monitoring: Continuous security monitoring
                
                Technologies:
                - Identity and Access Management (IAM)
                - Privileged Access Management (PAM)
                - Security Information and Event Management (SIEM)
                - Endpoint Detection and Response (EDR)
                """,
                "category": "zero_trust"
            },
            {
                "title": "Secure Coding Practices",
                "content": """
                Secure Coding Best Practices
                
                Input Validation:
                - Sanitize all user inputs
                - Validate data types and ranges
                - Use parameterized queries
                - Implement proper error handling
                
                Authentication and Authorization:
                - Strong password policies
                - Multi-factor authentication
                - Session management
                - Role-based access control
                
                Data Protection:
                - Encrypt sensitive data
                - Secure data transmission (HTTPS/TLS)
                - Data masking and anonymization
                - Secure key management
                
                Error Handling:
                - Don't expose sensitive information
                - Log security events
                - Implement proper exception handling
                - Use secure logging practices
                """,
                "category": "secure_coding"
            }
        ]
        
        documents = []
        metadatas = []
        
        for i, doc in enumerate(security_docs):
            documents.append(doc["content"])
            metadatas.append({
                "source": "security_docs",
                "title": doc["title"],
                "category": doc["category"],
                "type": "security",
                "index": i,
                "collection": "security"
            })
        
        if documents:
            self.rag_systems["security"].add_documents(documents, metadatas)
            print(f"✅ Added {len(documents)} Security documents")
    
    def ingest_data_science_datasets(self):
        """Ingest data science and analytics datasets"""
        print("📊 Ingesting Data Science datasets...")
        
        try:
            # Load a data science dataset
            dataset = load_dataset("tatsu-lab/alpaca", split="train[:500]")
            
            # Filter for data science related content
            data_science_docs = []
            for example in dataset:
                if any(keyword in example.get('instruction', '').lower() for keyword in 
                      ['data', 'analysis', 'statistics', 'visualization', 'pandas', 'numpy', 'matplotlib']):
                    text = f"Instruction: {example['instruction']}\nOutput: {example['output']}"
                    data_science_docs.append(text)
            
            documents = []
            metadatas = []
            
            for i, doc in enumerate(data_science_docs[:200]):  # Limit to 200
                documents.append(doc)
                metadatas.append({
                    "source": "huggingface",
                    "dataset": "alpaca",
                    "type": "data_science",
                    "index": i,
                    "collection": "data_science"
                })
            
            if documents:
                self.rag_systems["data_science"].add_documents(documents, metadatas)
                print(f"✅ Added {len(documents)} Data Science documents")
            
        except Exception as e:
            print(f"❌ Error ingesting data science data: {e}")
    
    def run_specialized_ingestion(self):
        """Run specialized data ingestion"""
        print("🎯 Starting Specialized Data Ingestion")
        print("=" * 45)
        
        start_time = time.time()
        
        # Ingest specialized datasets
        self.ingest_ai_ml_datasets()
        self.ingest_devops_datasets()
        self.ingest_security_datasets()
        self.ingest_data_science_datasets()
        
        # Calculate stats
        end_time = time.time()
        duration = end_time - start_time
        
        total_docs = 0
        print(f"\n📊 Specialized Collections Created:")
        for name, rag in self.rag_systems.items():
            try:
                collections = rag.client.list_collections()
                for collection in collections:
                    if collection.name == rag.collection_name:
                        count = collection.count()
                        total_docs += count
                        print(f"   - {name}: {count} documents")
            except:
                print(f"   - {name}: Collection created")
        
        print(f"\n🎉 Specialized Ingestion Complete!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Total Documents: {total_docs}")
        
        return total_docs

def main():
    """Main function"""
    print("🎯 Specialized RAG Data Ingestion")
    print("=" * 35)
    
    # Initialize specialized ingestion
    ingestion = SpecializedIngestion()
    
    # Run specialized ingestion
    total_docs = ingestion.run_specialized_ingestion()
    
    print(f"\n💡 Specialized Collections Available:")
    print(f"   - AI/ML Knowledge: Technical AI/ML content")
    print(f"   - DevOps Knowledge: Infrastructure and deployment")
    print(f"   - Security Knowledge: Cybersecurity and best practices")
    print(f"   - Data Science Knowledge: Analytics and data processing")
    
    print(f"\n🚀 Next Steps:")
    print(f"1. 🌐 View all collections: python /Users/andrejsp/ai/scripts/start_web_interfaces.py")
    print(f"2. 🔍 Test domain-specific queries")
    print(f"3. 📊 Monitor collection performance")
    print(f"4. 🎯 Add more specialized content as needed")

if __name__ == "__main__":
    main()