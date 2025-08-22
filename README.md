# CAS番号示性式検索アプリ

このリポジトリは、Excelファイルに記載されたCAS番号を元に、PubChemのPUG REST APIを用いて示性式（Molecular Formula）と分子量（Molecular Weight）を自動取得するアプリケーションです。Streamlitを利用しており、ブラウザ上でファイルをアップロードするだけで、結果を取得してダウンロードすることができます。

---

## 特長

- **簡単な操作** – Excelファイルをアップロードするだけで処理が始まります。
- **非登録物質対応** – PubChemに登録されていない物質や混合物（石綿等）の場合は手動定義値を参照し、無いものは空欄として処理します。
- **一括取得** – スレッドプールにより複数のCAS番号を効率的に検索します。

---

## 必要条件

- Python 3.8以上
- `pip install -r requirements.txt` で依存ライブラリを一括インストール可能

---

## インストール

```bash
git clone https://github.com/yourusername/cas-lookup-app.git
cd cas-lookup-app
pip install -r requirements.txt
```

---

## 実行方法

```bash
streamlit run cas_lookup_app.py
```

実行するとブラウザが自動で起動します。

---

## 使い方

1. Excelファイルをアップロード（1列目にCAS番号が記載された形式）
2. アプリが自動で各CAS番号を検索し、MFとMWを取得
3. 結果を含むExcelファイルをダウンロード可能

---

## ファイル構成

- `cas_lookup_app.py` – メインアプリケーションコード（Streamlit UI含む）
- `requirements.txt` – 必要ライブラリ一覧
- `README.md` – このファイル
- `.gitignore` – Git管理除外ファイル

---

## 注意点

- PubChemに登録されていないCAS番号に対しては結果が空欄になります（手動定義されていない場合）
- APIのレスポンスによっては一部遅延することがあります
