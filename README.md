# cas
CAS番号示性式検索アプリ

このリポジトリは、Excelファイルに記載されたCAS番号を元に、PubChemのPUG REST APIを用いて示性式（Molecular Formula）と分子量（Molecular Weight）を自動取得するアプリケーションです。Streamlitを利用しており、ブラウザ上でファイルをアップロードするだけで、結果を取得してダウンロードすることができます。

特長

簡単な操作 – Excelファイルをアップロードするだけで処理が始まります。

非登録物質対応 – PubChemに登録されていない物質や混合物（石綿等）の場合は手動定義値を参照し、無いものは空欄として処理します。

一括取得 – スレッドプールにより複数のCAS番号を効率的に検索します。

必要条件

Python 3.8以上

Streamlit

Pandas

Requests

openpyxl

依存関係は requirements.txt に記載されています。以下のコマンドでインストールできます。

pip install -r requirements.txt

使い方

リポジトリをクローンして必要なライブラリをインストールします。

git clone <リポジトリのURL>
cd <リポジトリディレクトリ>
pip install -r requirements.txt


Streamlitを起動します。

streamlit run cas_lookup_app.py


ブラウザが開くので、処理したいExcelファイル（1列目にCAS番号が記載されているもの）をアップロードします。

検索結果が表形式で表示され、「結果をダウンロード」ボタンからExcelファイルをダウンロードできます。

ファイル構成

cas_lookup_app.py – Streamlitアプリ本体。CAS番号を検索して結果を表示・ダウンロードします。

requirements.txt – アプリケーション実行に必要なPythonパッケージを記載しています。

.gitignore – Gitで追跡しないファイルやディレクトリを指定しています。

ライセンス

このプロジェクトのライセンスはMITライセンスです。詳細は LICENSE ファイルをご覧ください。
