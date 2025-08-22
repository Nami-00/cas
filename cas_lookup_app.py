"""
Streamlit アプリ: CAS番号から示性式（分子式）と分子量を検索し、
Excelファイルに結果を付加してダウンロードできるようにします。

このスクリプトを実行することで、ユーザーはExcelファイルをアップロードし、
1列目に記載されたCAS番号をPubChemのPUG REST APIで検索して、
示性式（Molecular Formula）と分子量（Molecular Weight）を取得します。
情報が存在しない場合は値を空欄のままにします。

使い方:
1. ターミナルで以下を実行してStreamlitサーバーを起動します。
   ```bash
   streamlit run cas_lookup_app.py
   ```
2. ブラウザが自動的に開かない場合は表示されたURLをブラウザに入力します。
3. アプリ上でExcelファイル（.xlsx）をアップロードすると、
   CAS番号の列を読み込み、示性式と分子量を取得します。
4. 処理結果は画面上に表示され、「ダウンロード」ボタンからExcel形式で保存できます。

注意:
PubChemのAPIは1秒間に多数のリクエストを送るとエラーが発生することがあります。
そのため、このアプリではスレッドプールを使って同時に4件まで処理するよう制限しています。

作者: ChatGPT
"""

import io
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 注意: Streamlitはアプリを実行する際にのみ必要です。テストや関数の単体利用では
# importしなくても問題ありません。そのため、メイン関数内でimportします。


def fetch_cas_info(cas: str, manual_data: dict) -> tuple[str | None, float | None]:
    """
    個々のCAS番号についてPubChemのAPIから示性式と分子量を取得します。
    情報が存在しない場合は (None, None) を返します。

    Args:
        cas (str): CAS番号
        manual_data (dict): 手動で定義したCAS番号とその示性式・分子量の辞書

    Returns:
        tuple[str|None, float|None]: (示性式, 分子量)
    """
    # 手動データがある場合はそれを優先
    if cas in manual_data:
        return manual_data[cas]

    # PubChem PUG REST API のエンドポイント
    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/"
        "property/MolecularFormula,MolecularWeight/JSON"
    )

    # 最大3回リトライして安定性を確保
    for _ in range(3):
        try:
            response = requests.get(url, timeout=10)
            # 200 OK の場合はJSONを解析
            if response.status_code == 200:
                data = response.json()
                properties = data.get("PropertyTable", {}).get("Properties", [])
                if properties:
                    prop = properties[0]
                    formula = prop.get("MolecularFormula")
                    weight_raw = prop.get("MolecularWeight")
                    # 重量は文字列として返る場合があるのでfloatに変換
                    try:
                        weight = float(weight_raw)
                    except (TypeError, ValueError):
                        weight = None
                    return formula, weight
            # エラー時は少し待機してリトライ
        except Exception:
            pass
    # 取得できない場合はNone
    return None, None


def process_file(file: io.BytesIO) -> pd.DataFrame:
    """
    アップロードされたExcelファイルを読み込み、CAS番号から
    示性式・分子量を取得して新しい列として追加します。

    Args:
        file (io.BytesIO): アップロードされたファイルオブジェクト

    Returns:
        pd.DataFrame: 処理後のデータフレーム
    """
    # Excelファイルを読み込む
    df = pd.read_excel(file)
    if df.empty:
        return df
    # 1列目をCAS番号として読み込む
    cas_series = df.iloc[:, 0].astype(str).fillna("")

    # Asbestosなどの既知のCAS番号について手動データを用意
    manual_data: dict[str, tuple[str | None, float | None]] = {
        "77536-66-4": ("Ca2Fe5H2O24Si8", 970.1),
        "77536-67-5": ("H2Mg7O24Si8", 780.82),
        "77536-68-6": ("Ca2H2Mg5O24Si8", 812.37),
        "13768-00-8": ("Fe2H16Mg3Na2O24Si8+14", 855.38),
        "17068-78-9": ("Fe7H2O24Si8", 1001.6),
        "12172-67-7": ("Ca2Fe5H2O24Si8", 970.1),
        "12172-73-5": ("Fe7H2O24Si8", 1001.6),
        "12001-28-4": ("Fe2H16Mg3Na2O24Si8+14", 855.38),
        "12001-29-5": ("H4Mg3O9Si2", 277.11),
        "1332-21-4": (None, None),  # Asbestos全般は一定の組成がなく定義できない
        "132207-32-0": ("Ca2H2Mg5O24Si8", 812.37),
        "132207-33-1": ("Fe2H16Mg3Na2O24Si8+14", 855.38),
        "14567-73-8": ("H4Mg3O9Si2", 277.11),
        "12185-10-3": ("P4", 123.8950480),
        "25512-42-9": ("C12H8Cl2", 223.09792),
    }

    # 検索結果を格納するリスト
    formulas: list[str | None] = [None] * len(cas_series)
    weights: list[float | None] = [None] * len(cas_series)

    # スレッドプールで並行して検索
    with ThreadPoolExecutor(max_workers=4) as executor:
        # 辞書を用いて、各FutureとCAS番号の対応付けを保持
        future_to_index = {}
        for idx, cas in enumerate(cas_series):
            # 空文字列の場合は検索しない
            if not cas:
                continue
            future = executor.submit(fetch_cas_info, cas, manual_data)
            future_to_index[future] = idx

        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                formula, weight = future.result()
            except Exception:
                formula, weight = None, None
            formulas[idx] = formula
            weights[idx] = weight

    # 結果を新しい列として追加
    df["示性式"] = formulas
    df["分子量"] = weights
    return df


def main() -> None:
    """Streamlitアプリのメイン関数。

    Streamlitはこの関数内でインポートします。これにより、他の関数を単体で
    利用する場合やテスト環境でStreamlitがインストールされていない場合に
    インポートエラーを避けることができます。
    """
    # Streamlit のインポートはここで実行
    import streamlit as st

    st.title("CAS番号の示性式・分子量取得アプリ")
    st.write(
        "Excelファイル（.xlsx）をアップロードすると、1列目のCAS番号をPubChemのAPIで検索して\n"
        "示性式（Molecular Formula）と分子量（Molecular Weight）を取得します。\n"
        "エクセルファイルの1列目にCAS番号のリストを作成してください（1行目は「CAS No.」項目名です）"
    )

    uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])
    if uploaded_file is not None:
        # ファイルを処理
        with st.spinner("ファイルを処理しています..."):
            result_df = process_file(uploaded_file)

        st.success("処理が完了しました。下記に結果を表示します。")
        st.dataframe(result_df)

        # Excelファイルとしてダウンロードできるようにする
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            result_df.to_excel(writer, index=False)
        st.download_button(
            label="結果をダウンロード",
            data=output.getvalue(),
            file_name="cas_lookup_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


if __name__ == "__main__":
    main()