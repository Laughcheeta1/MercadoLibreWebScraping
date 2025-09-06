from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from logging_config import set_up_logger
from dotenv import load_dotenv

logger = set_up_logger(__name__)
load_dotenv()

class MongoManager:
    def __init__(self, *, connection_string: str = None, database_name: str = None):
        """
        Initialize MongoDB connection manager
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database to use
        """
        import os
        
        # Use environment variables as defaults if not provided
        if connection_string is None:
            connection_string = os.getenv('MONGO_CONNECTION_STRING')
        if database_name is None:
            database_name = os.getenv('DATABASE_NAME')
            
        if not connection_string:
            raise ValueError("MongoDB connection string must be provided either as parameter or MONGO_CONNECTION_STRING environment variable")
        if not database_name:
            raise ValueError("Database name must be provided either as parameter or DATABASE_NAME environment variable")
            
        logger.info(f"Initializing MongoDB connection to database: {database_name}")
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[database_name]
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"Failed to establish MongoDB connection: {e}")
            raise

    def insert_many(self, documents: List[Dict[str, Any]], collection_name: str="Items") -> List[str]:
        """
        Insert multiple documents into the specified collection
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
            
        Returns:
            List of document IDs
        """
        logger.info(f"Inserting multiple documents into collection: {collection_name}")
        logger.debug(f"Documents: {documents}")
        
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            document_ids = [str(doc_id) for doc_id in result.inserted_ids]
            logger.info(f"Successfully inserted {len(document_ids)} documents")
            return document_ids
        except Exception as e:
            logger.error(f"Failed to insert documents into collection {collection_name}: {e}")
            raise

    def create_document(self, document: Dict[str, Any], collection_name: str="Items") -> str:
        """
        Create a new document in the specified collection
        
        Args:
            collection_name: Name of the collection
            document: Document data to insert
            
        Returns:
            String representation of the inserted document's ObjectId
        """
        logger.info(f"Creating document in collection: {collection_name}")
        logger.debug(f"Document data: {document}")
        
        try:
            collection = self.db[collection_name]
            
            # Add timestamp if not present
            if 'created_at' not in document:
                document['created_at'] = datetime.now(timezone.utc)
            
            result = collection.insert_one(document)
            document_id = str(result.inserted_id)
            logger.info(f"Document created successfully with ID: {document_id}")
            return document_id
        except Exception as e:
            logger.error(f"Failed to create document in collection {collection_name}: {e}")
            raise
    
    def find_document(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find a single document in the collection
        
        Args:
            collection_name: Name of the collection
            query: Query to match documents
            
        Returns:
            Found document or None if not found
        """
        logger.info(f"Finding document in collection: {collection_name}")
        logger.debug(f"Query: {query}")
        
        try:
            collection = self.db[collection_name]
            result = collection.find_one(query)
            
            if result:
                logger.info("Document found successfully")
                logger.debug(f"Found document: {result}")
            else:
                logger.info("No document found matching the query")
                
            return result
        except Exception as e:
            logger.error(f"Failed to find document in collection {collection_name}: {e}")
            raise
    
    def find_documents(self, collection_name: str, query: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        Find multiple documents in the collection
        
        Args:
            collection_name: Name of the collection
            query: Query to match documents (empty dict for all documents)
            limit: Maximum number of documents to return
            
        Returns:
            List of found documents
        """
        logger.info(f"Finding documents in collection: {collection_name}")
        logger.debug(f"Query: {query}, Limit: {limit}")
        
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {})
            
            if limit:
                cursor = cursor.limit(limit)
                
            results = list(cursor)
            logger.info(f"Found {len(results)} documents")
            logger.debug(f"Documents: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to find documents in collection {collection_name}: {e}")
            raise
    
    def update_document(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """
        Update a single document in the collection
        
        Args:
            collection_name: Name of the collection
            query: Query to match the document to update
            update: Update operations to apply
            
        Returns:
            True if document was updated, False otherwise
        """
        logger.info(f"Updating document in collection: {collection_name}")
        logger.debug(f"Query: {query}, Update: {update}")
        
        try:
            collection = self.db[collection_name]
            
            # Add updated timestamp
            if '$set' not in update:
                update['$set'] = {}
            update['$set']['updated_at'] = datetime.utcnow()
            
            result = collection.update_one(query, update)
            updated = result.modified_count > 0
            
            if updated:
                logger.info("Document updated successfully")
            else:
                logger.info("No document was updated (either not found or no changes made)")
                
            return updated
        except Exception as e:
            logger.error(f"Failed to update document in collection {collection_name}: {e}")
            raise
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """
        Delete a single document from the collection
        
        Args:
            collection_name: Name of the collection
            query: Query to match the document to delete
            
        Returns:
            True if document was deleted, False otherwise
        """
        logger.info(f"Deleting document from collection: {collection_name}")
        logger.debug(f"Query: {query}")
        
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            deleted = result.deleted_count > 0
            
            if deleted:
                logger.info("Document deleted successfully")
            else:
                logger.info("No document was deleted (not found)")
                
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete document from collection {collection_name}: {e}")
            raise
    
    def close_connection(self):
        """Close the MongoDB connection"""
        logger.info("Closing MongoDB connection")
        try:
            self.client.close()
            logger.info("MongoDB connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
            raise
