import os
import logging
import base64
import requests
import time
import pandas as pd

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, time.strftime("%Y-%m-%d_%H-%M-%S.log"))

def get_logger(scope):
    logger = logging.getLogger(scope)

    # if os.environ["APP_ENV"] in ["local", "dev", "stage"]:
    #     logging.basicConfig(level=logging.DEBUG)
    # else:
    logging.basicConfig(level=logging.INFO)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

logger = get_logger(__name__)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def read_excel_file(excel_file_path, max_rows=100, max_cols=50):
    """
    Read an Excel file and return its content as a formatted string.
    
    Args:
        excel_file_path: Path to the Excel file
        max_rows: Maximum number of rows to include (to avoid overly long prompts)
        max_cols: Maximum number of columns to include
    
    Returns:
        A formatted string representation of the Excel file content
    """
    try:
        if not os.path.exists(excel_file_path):
            return f"Error: Excel file not found at path: {excel_file_path}"
        
        # Read all sheets from the Excel file
        excel_file = pd.ExcelFile(excel_file_path)
        sheet_names = excel_file.sheet_names
        
        result = []
        result.append(f"Excel file: {excel_file_path}")
        result.append(f"Number of sheets: {len(sheet_names)}")
        result.append("")
        
        for sheet_name in sheet_names:
            result.append(f"Sheet: '{sheet_name}'")
            result.append("-" * 50)
            
            # Read the sheet
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            
            # Limit the size
            original_shape = df.shape
            df = df.iloc[:max_rows, :max_cols]
            
            # Convert to string representation
            if df.empty:
                result.append("(Empty sheet)")
            else:
                result.append(f"Shape: {original_shape[0]} rows × {original_shape[1]} columns")
                if original_shape[0] > max_rows or original_shape[1] > max_cols:
                    result.append(f"(Showing first {min(max_rows, original_shape[0])} rows and {min(max_cols, original_shape[1])} columns)")
                result.append("")
                result.append(df.to_string(index=True, max_rows=max_rows, max_cols=max_cols))
            
            result.append("")
            result.append("")
        
        return "\n".join(result)
    
    except Exception as e:
        logger.error(f"Error reading Excel file {excel_file_path}: {str(e)}")
        return f"Error reading Excel file: {str(e)}"
