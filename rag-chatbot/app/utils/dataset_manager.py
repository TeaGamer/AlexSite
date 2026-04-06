"""Dataset utilities for handling CSV/JSON data"""
import json
import csv
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import uuid
from datetime import datetime


class DatasetManager:
    """Manager for handling study program datasets"""
    
    def __init__(self, dataset_path: str = "./datasets"):
        """Initialize dataset manager"""
        self.dataset_path = Path(dataset_path)
        self.dataset_path.mkdir(parents=True, exist_ok=True)
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file"""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise Exception(f"Error loading CSV: {str(e)}")
    
    def load_json(self, file_path: str) -> List[Dict]:
        """Load JSON file (array of objects)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            raise Exception(f"Error loading JSON: {str(e)}")
    
    def load_jsonl(self, file_path: str) -> List[Dict]:
        """Load JSONL file (JSON Lines format)"""
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            return data
        except Exception as e:
            raise Exception(f"Error loading JSONL: {str(e)}")
    
    def dataset_to_chunks(
        self,
        data: List[Dict],
        text_column: str = "content",
        chunk_size: int = 1000,
        overlap: int = 200,
        metadata_fields: Optional[List[str]] = None
    ) -> List[Tuple[str, Dict]]:
        """
        Convert dataset entries to chunks with metadata
        
        Args:
            data: List of dictionaries from dataset
            text_column: Column name containing the text
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            metadata_fields: Additional fields to include in metadata
        
        Returns:
            List of (chunk_text, metadata) tuples
        """
        chunks_with_metadata = []
        
        for item in data:
            if text_column not in item:
                continue
            
            text = str(item[text_column])
            
            # Extract metadata
            metadata = {
                "source": item.get("title", "Unknown"),
                "document_id": str(uuid.uuid4()),
            }
            
            # Add additional metadata fields
            if metadata_fields:
                for field in metadata_fields:
                    if field in item:
                        metadata[field] = item[field]
            
            # Split text into chunks
            text_chunks = self._split_text_into_chunks(text, chunk_size, overlap)
            
            for i, chunk in enumerate(text_chunks):
                chunk_metadata = {
                    **metadata,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks)
                }
                chunks_with_metadata.append((chunk, chunk_metadata))
        
        return chunks_with_metadata
    
    @staticmethod
    def _split_text_into_chunks(
        text: str,
        chunk_size: int = 1000,
        overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk.strip())
            start = end - overlap
        
        return [c for c in chunks if len(c.strip()) > 0]
    
    def create_training_dataset(
        self,
        data: List[Dict],
        question_column: str = "question",
        answer_column: str = "answer",
        output_path: Optional[str] = None
    ) -> str:
        """
        Create training dataset in format suitable for fine-tuning
        
        Args:
            data: Dataset with question-answer pairs
            question_column: Column containing questions
            answer_column: Column containing answers
            output_path: Path to save training data
        
        Returns:
            Path to saved training file
        """
        if output_path is None:
            output_path = str(self.dataset_path / f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in data:
                if question_column in item and answer_column in item:
                    training_item = {
                        "prompt": f"{item[question_column]}",
                        "completion": f" {item[answer_column]}"
                    }
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
        
        return output_path
    
    def validate_dataset(self, data: List[Dict], required_columns: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate dataset structure
        
        Args:
            data: Dataset to validate
            required_columns: Required column names
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if not data:
            errors.append("Dataset is empty")
            return False, errors
        
        # Check first item for required columns
        first_item = data[0]
        for col in required_columns:
            if col not in first_item:
                errors.append(f"Missing required column: {col}")
        
        return len(errors) == 0, errors
    
    def convert_csv_to_jsonl(
        self,
        csv_path: str,
        jsonl_path: str = None,
        columns: Optional[List[str]] = None
    ) -> str:
        """
        Convert CSV to JSONL format
        
        Args:
            csv_path: Path to CSV file
            jsonl_path: Output path for JSONL
            columns: Specific columns to include
        
        Returns:
            Path to created JSONL file
        """
        if jsonl_path is None:
            csv_name = Path(csv_path).stem
            jsonl_path = str(self.dataset_path / f"{csv_name}.jsonl")
        
        df = self.load_csv(csv_path)
        
        if columns:
            df = df[columns]
        
        with open(jsonl_path, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                f.write(json.dumps(row.to_dict(), ensure_ascii=False) + '\n')
        
        return jsonl_path
    
    def sample_dataset(
        self,
        data: List[Dict],
        sample_size: int = 10,
        random: bool = True
    ) -> List[Dict]:
        """
        Sample from dataset
        
        Args:
            data: Full dataset
            sample_size: Number of samples
            random: Whether to sample randomly
        
        Returns:
            Sampled data
        """
        if random:
            import random as rnd
            return rnd.sample(data, min(sample_size, len(data)))
        else:
            return data[:sample_size]
