from pathlib import Path
import numpy as np
import pandas as pd

# Lokasi file data
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_FOLDER / "data/raw/automobileEDA_dirty_training.csv"
PROCESSED_FILE = PROJECT_FOLDER / "data/processed/automobileEDA_processed.csv"


def load_data():
    """Membaca file CSV mentah."""
    return pd.read_csv(RAW_FILE)


def inspect_data(df):
    """Menampilkan kondisi awal data."""
    print("\n=== PEMERIKSAAN DATA ===")

    print("\n5 baris pertama:")
    print(df.head().to_string())

    print("\nJumlah baris dan kolom:", df.shape)

    print("\nNama kolom:")
    print(list(df.columns))

    print("\nTipe data:")
    print(df.dtypes)

    print("\nJumlah data kosong:")
    print(df.isna().sum())

    print("\nJumlah baris duplikat:", df.duplicated().sum())

    print("\nNilai unik kolom kategori:")
    for column in ["make", "num-of-doors", "body-style", "drive-wheels", "fuel-system", "horsepower-binned"]:
        print(column, ":", df[column].unique().tolist())

    print("\nRingkasan angka (untuk mengecek nilai tidak wajar):")
    print(df.describe().to_string())


def clean_data(df):
    """Membersihkan data."""
    clean = df.copy()

    # 1. Rapikan teks: hapus spasi berlebih dan jadikan huruf kecil
    for column in ["make", "body-style", "drive-wheels", "fuel-system"]:
        clean[column] = clean[column].str.strip().str.lower()

    # 2. Samakan format tanggal (ada 4 format di data mentah)
    dates = clean["transaction_date"]
    fixed_dates = pd.to_datetime(dates, format="%Y-%m-%d", errors="coerce")
    fixed_dates = fixed_dates.fillna(pd.to_datetime(dates, format="%d/%m/%Y", errors="coerce"))
    fixed_dates = fixed_dates.fillna(pd.to_datetime(dates, format="%m-%d-%Y", errors="coerce"))
    fixed_dates = fixed_dates.fillna(pd.to_datetime(dates, format="%d-%b-%Y", errors="coerce"))
    clean["transaction_date"] = fixed_dates

    # 3. Hapus baris duplikat
    clean = clean.drop_duplicates()

    # 4. Isi data kosong pada kolom kategori
    clean["make"] = clean["make"].fillna("unknown")
    clean["num-of-doors"] = clean["num-of-doors"].fillna("four")  # nilai paling sering muncul
    clean["horsepower-binned"] = clean["horsepower-binned"].fillna("High")  # horsepower baris ini 262

    # 5. Isi data kosong pada kolom angka dengan median (nilai tengah)
    for column in ["stroke", "horsepower", "price"]:
        clean[column] = clean[column].fillna(np.nanmedian(clean[column]))

    return clean


def show_cleaning_result(before, after):
    """Menampilkan perbandingan sebelum dan sesudah cleaning."""
    print("\n=== HASIL CLEANING ===")
    print("Jumlah baris:", len(before), "->", len(after))
    print("Jumlah data kosong:", before.isna().sum().sum(), "->", after.isna().sum().sum())
    print("Baris duplikat yang dihapus:", len(before) - len(after))

    print("Kolom yang berubah:")
    same_rows = before.loc[after.index]
    for column in before.columns:
        if not same_rows[column].equals(after[column]):
            print("-", column)


def transform_data(df):
    """Mengubah skala angka dan mengubah kategori menjadi angka."""
    result = df.copy()

    # Min-Max Scaling: mengubah angka ke rentang 0 sampai 1
    for column in ["price", "horsepower"]:
        smallest = np.min(result[column])
        largest = np.max(result[column])
        result[column + "_scaled"] = (result[column] - smallest) / (largest - smallest)

    # One-hot encoding: setiap kategori menjadi satu kolom berisi 0 atau 1
    body_style_columns = pd.get_dummies(result["body-style"], prefix="body-style", dtype=int)
    result = pd.concat([result, body_style_columns], axis=1)

    print("\n=== HASIL TRANSFORMASI ===")
    print(result[["price", "price_scaled", "horsepower", "horsepower_scaled"]].head(3).to_string())
    print(result[["body-style"] + list(body_style_columns.columns)].head(4).to_string())

    return result


def save_data(df):
    """Menyimpan hasil sebagai file CSV baru."""
    df.to_csv(PROCESSED_FILE, index=False)
    print("\n=== SELESAI ===")
    print("Ukuran akhir:", df.shape)
    print("File tersimpan di:", PROCESSED_FILE)


def run_pipeline():
    """Menjalankan semua tahap secara berurutan."""
    raw_data = load_data()                       # Extract
    inspect_data(raw_data)                       # Transform
    clean = clean_data(raw_data)
    show_cleaning_result(raw_data, clean)
    processed_data = transform_data(clean)
    save_data(processed_data)                    # Load


if __name__ == "__main__":
    run_pipeline()
