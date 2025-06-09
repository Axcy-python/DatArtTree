from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import os.path
import pickle
import requests
import io
import pandas as pd
from typing import Literal, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
import openai
from cryptography.fernet import Fernet
import json
import threading
import time
                

class GoogleAPI:
    __SCOPES = [
        "https://www.googleapis.com/auth/drive.metadata.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    def __init__(self):
        self.__creds = self.__authorize_google()


    def __authorize_google(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'App/credentials.json', self.__SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds


    def get_user_info(self) -> dict:
        return requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            params={"alt": "json"},
            headers={"Authorization": f"Bearer {self.__creds.token}"}
        ).json()


    def get_list_sheets_files(self) -> list[dict]:
        service = build('drive', 'v3', credentials=self.__creds)
        results = service.files().list(
            q = (
                "mimeType='application/vnd.google-apps.spreadsheet' or "
                "mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or "
                "mimeType='application/vnd.ms-excel' or "
                "mimeType='text/csv'"
            ),
            pageSize=10,
            fields="files(id, name, modifiedTime, mimeType)"
        ).execute()
        files = results.get('files', [])
        return files
    

    def get_sheets_data(self, spreadsheet_id):
        service = build('sheets', 'v4', credentials=self.__creds)
    
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_title = spreadsheet['sheets'][0]['properties']['title']
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_title,
            majorDimension='ROWS'
        ).execute()
        
        values = result.get('values', [])
        return values
    

    def get_data_from_xls_csv(self, file_id: str) -> io.BytesIO:
        drive_service = build('drive', 'v3', credentials=self.__creds)
        request = drive_service.files().get_media(fileId=file_id)
        
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_io.seek(0)

        return file_io
    

class LocalFileAPI:
    SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

    def __init__(self):
        self.__file_path = None
        self.__file_type = None
        self.__file_bytes = None


    def load_file(self, file_path: str):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}")

        with open(file_path, "rb") as f:
            file_data = f.read()

        self.__file_path = file_path
        self.__file_type = "csv" if ext == ".csv" else "xlsx"
        self.__file_bytes = io.BytesIO(file_data)


    def get_file_bytes(self) -> io.BytesIO:
        if self.__file_bytes is None:
            raise RuntimeError("No file loaded.")
        self.__file_bytes.seek(0)
        return self.__file_bytes


    def get_file_type(self) -> str:
        if self.__file_type is None:
            raise RuntimeError("No file loaded.")
        return self.__file_type


    def clear(self):
        """Викликати при виході з програми або при завантаженні нового файлу."""
        self.__file_path = None
        self.__file_type = None
        self.__file_bytes = None
    

class Data:
    """
    Клас для роботи з даними за допомогою pandas.
    Підтримує:
      - байтовий потік (BytesIO) із .csv/.xlsx файлу,
      - дані у вигляді списку списків (наприклад, з Google Sheets).
    """

    def __init__(
        self,
        file_data: Optional[io.BytesIO] = None,
        file_type: Literal['xlsx', 'xls', 'csv'] = 'xlsx',
        data_from_list: Optional[list[list]] = None
    ):
        self.__df = None

        if data_from_list:
            self.__load_from_list(data_from_list)
        elif file_data:
            self.__load_from_file(file_data, file_type.lower())
        else:
            raise ValueError("Потрібно передати або file_data, або data_from_list.")


    def __load_from_file(self, file_data: io.BytesIO, file_type: str):
        file_data.seek(0)
        if file_type == "csv":
            self.__df = pd.read_csv(file_data)
        elif file_type in ("xlsx", "xls"):
            self.__df = pd.read_excel(file_data)
        else:
            raise ValueError(f"Непідтримуваний тип файлу: {file_type}")


    def __load_from_list(self, data: list[list]):
        if not data or not isinstance(data[0], list):
            raise ValueError("Невірний формат даних: очікується список списків.")
        headers = data[0]
        rows = data[1:]
        self.__df = pd.DataFrame(rows, columns=headers)


    def get_dataframe(self) -> pd.DataFrame:
        """Повертає повний DataFrame."""
        return self.__df


    def get_columns(self) -> list[str]:
        """Повертає список назв колонок."""
        return self.__df.columns.tolist()


    def get_shape(self) -> tuple[int, int]:
        """Повертає розмір таблиці: (рядки, колонки)."""
        return self.__df.shape


    def to_dict(self) -> list[dict]:
        """Повертає DataFrame у вигляді списку словників (records)."""
        return self.__df.to_dict(orient="records")


class DataPlot:
    def __init__(self, dataframe: pd.DataFrame):
        self.__df: pd.DataFrame = dataframe


    def __to_list(self, value):
        return value if isinstance(value, list) else [value]


    def __autopct_percent(self, pct):
        return f"{pct:.1f}%"


    def __autopct_value(self, pct, all_vals):
        total = sum(all_vals)
        val = round(pct * total / 100.0, 2)
        return f"{val}"


    def __autopct_combined(self, pct, all_vals):
        total = sum(all_vals)
        val = round(pct * total / 100.0, 2)
        return f"{val} ({pct:.1f}%)"


    def __autopct(self, mode: str, values):
        if mode == 'percent':
            return lambda pct: self.__autopct_percent(pct)
        elif mode == 'value':
            return lambda pct: self.__autopct_value(pct, values)
        elif mode == 'combined':
            return lambda pct: self.__autopct_combined(pct, values)
        else:
            raise ValueError(f"Невідомий режим autopct: '{mode}'")


    def __aggregate(self, group_by, value_col: str, agg_func: str) -> pd.DataFrame:
        group_by = self.__to_list(group_by)
        return self.__df.groupby(group_by)[value_col].agg(agg_func)
    

    def clear(self) -> None:
        self.__df = None


    def bar_chart_plot(self, value_col: str, group_by=Union[str, list, None], agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        if value_col not in self._df.columns:
            raise ValueError(f"Колонка '{value_col}' не знайдена.")

        dtype = self._df[value_col].dtype
        plt.figure(figsize=(8, 5))

        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_bool_dtype(dtype):
            self._df[value_col].value_counts().plot(kind='bar', color='teal')
            plt.ylabel("Кількість")
            plt.xlabel(value_col)

        elif pd.api.types.is_numeric_dtype(dtype):
            if group_by:
                grouped = self.__aggregate(group_by, value_col, agg_func)
                grouped.plot(kind='bar', color='orange')
                plt.xlabel(', '.join(self.__to_list(group_by)))
                plt.ylabel(f"{agg_func} {value_col}")
            else:
                self._df[value_col].plot(kind='hist', bins=10, color='orange', edgecolor='black')
                plt.ylabel("Кількість")
                plt.xlabel(value_col)
        else:
            raise TypeError(f"Тип '{value_col}' не підтримується.")

        plt.title(f"Bar/Hist для '{value_col}'")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.show()


    def pie_chart_plot(self, group_by=Union[str, list, None], value_col=None, mode: Literal['percent', 'value', 'combined']='percent', agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        group_by = self.__to_list(group_by)
        for col in group_by:
            if col not in self._df.columns:
                raise ValueError(f"Колонка '{col}' не знайдена.")

        if value_col:
            if value_col not in self._df.columns or not pd.api.types.is_numeric_dtype(self._df[value_col]):
                raise TypeError(f"'{value_col}' має бути числовою.")
            data = self.__aggregate(group_by, value_col, agg_func)
        else:
            data = self._df.groupby(group_by).size()

        values = data.values
        labels = [' - '.join(map(str, idx)) if isinstance(idx, tuple) else str(idx) for idx in data.index]

        plt.figure(figsize=(6, 6))
        plt.pie(values, labels=labels, autopct=self.__autopct(mode, values), startangle=90, colors=plt.cm.Set3.colors)
        plt.title(f"Pie: {' + '.join(group_by)}" + (f" ({value_col})" if value_col else ""))
        plt.tight_layout()
        plt.show()


    def line_chart_plot(self, value_col: str, group_by=Union[str, list, None], agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        group_by = self.__to_list(group_by)
        data = self.__aggregate(group_by, value_col, agg_func)
        data.plot(kind='line', marker='o', linestyle='-', color='navy')
        plt.xlabel(', '.join(group_by))
        plt.ylabel(f"{agg_func} {value_col}")
        plt.title(f"Line chart: {agg_func} {value_col} по {', '.join(group_by)}")
        plt.grid(True)
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.show()


    def histogram_plot(self, value_col: str, group_by=Union[str, list, None], agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        if not pd.api.types.is_numeric_dtype(self._df[value_col]):
            raise TypeError(f"'{value_col}' має бути числовою.")

        if group_by:
            group_by = self.__to_list(group_by)
            data = self.__aggregate(group_by, value_col, agg_func)
        else:
            data = self._df[value_col]

        plt.figure(figsize=(8, 5))
        plt.hist(data, bins='auto', color='skyblue', edgecolor='black')
        plt.xlabel(value_col)
        plt.ylabel("Кількість")
        plt.title("Гістограма")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def box_plot(self, value_col: str, group_by=Union[str, list, None]):
        if not pd.api.types.is_numeric_dtype(self._df[value_col]):
            raise TypeError(f"'{value_col}' має бути числовою.")

        plt.figure(figsize=(8, 5))
        if group_by:
            group_by = self.__to_list(group_by)
            self._df.boxplot(column=value_col, by=group_by, grid=False)
            plt.title(f"Box plot '{value_col}' by {' + '.join(group_by)}")
            plt.suptitle("")
            plt.xlabel(', '.join(group_by))
        else:
            plt.boxplot(self._df[value_col])
            plt.title(f"Box plot '{value_col}'")
            plt.xticks([1], [value_col])

        plt.ylabel(value_col)
        plt.tight_layout()
        plt.show()


    def scatter_plot(self, x_col: str, y_col: str, group_by=Union[str, list, None], agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        if not all(pd.api.types.is_numeric_dtype(self._df[col]) for col in [x_col, y_col]):
            raise TypeError("Обидві колонки мають бути числовими.")

        if group_by:
            group_by = self.__to_list(group_by)
            x_data = self.__aggregate(group_by, x_col, agg_func)
            y_data = self.__aggregate(group_by, y_col, agg_func)
            data = pd.DataFrame({x_col: x_data, y_col: y_data})
        else:
            data = self._df[[x_col, y_col]]

        plt.figure(figsize=(8, 5))
        plt.scatter(data[x_col], data[y_col], color='purple', alpha=0.7, edgecolor='black')
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(f"Scatter: '{y_col}' vs '{x_col}'" + (f" ({agg_func})" if group_by else ""))
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def heatmap_plot(self, x_col: str, y_col: str, value_col: str, agg_func: Literal['mean', 'sum', 'max', 'min', 'median', 'all'] = 'mean'):
        if not pd.api.types.is_numeric_dtype(self._df[value_col]):
            raise TypeError(f"'{value_col}' має бути числовою.")

        grouped = self._df.pivot_table(index=y_col, columns=x_col, values=value_col, aggfunc=agg_func)
        plt.figure(figsize=(10, 6))
        sns.heatmap(grouped, annot=True, fmt=".1f", cmap='coolwarm', linewidths=.5)
        plt.title(f"Heatmap: {agg_func} {value_col} по {x_col} і {y_col}")
        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.tight_layout()
        plt.show()



class AIAgent:
    SECRET_PATH: str = ".venv/.secrets.json"
    KEY_PATH: str = ".venv/.secret.key"
    GPT_MODELS: tuple = ("gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo-0125")

    def __init__(self):
        self.openai_model = "gpt-3.5-turbo"
        self.token: str = None

        self.fernet = self.__load_or_create_key()
        self.__load_tokens()

        if self.token:
            openai.api_key = self.token


    def __load_or_create_key(self) -> Fernet:
        os.makedirs(".venv", exist_ok=True)
        if not os.path.exists(self.KEY_PATH):
            key = Fernet.generate_key()
            with open(self.KEY_PATH, "wb") as f:
                f.write(key)
        else:
            with open(self.KEY_PATH, "rb") as f:
                key = f.read()
        return Fernet(key)


    def __load_tokens(self):
        if os.path.exists(self.SECRET_PATH):
            with open(self.SECRET_PATH, "r") as f:
                data = json.load(f)
            if "openai" in data:
                self.token = self.fernet.decrypt(data["openai"].encode()).decode()
                openai.api_key = self.token


    def keycrypt(self, openai_key: str = None):
        data = {}
        if openai_key:
            self.token = openai_key
            openai.api_key = openai_key
            data["openai"] = self.fernet.encrypt(openai_key.encode()).decode()
    
        with open(self.SECRET_PATH, "w") as f:
            json.dump(data, f)


    def get_analyze(self, data: Union[list, dict, tuple, pd.DataFrame]) -> str:
        if self.token:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Ти помічник. Аналізуй дані стисло та зрозуміло."},
                        {"role": "user", "content": "Проаналізуй ці дані: " + str(data)}
                    ]
                )
                return response['choices'][0]['message']['content']
            except Exception as e:
                return f"[GPT] Помилка API: {str(e)}"
            

    def run_analysis_thread(self, data):
        threading.Thread(target=self.analyze_and_display, args=(data,), daemon=True).start()


    def analyze_and_display(self, data, output_widget):
        result = self.get_analyze(data)
        output_widget.after(0, lambda: output_widget.insert("end", result + "\n"))
    