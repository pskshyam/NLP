
def get_paragraph_ranges(len_df_original_text, df_headers_information):
    categories_range = {"p": [], "w": [], "i":[], "t":[]}
    df_headers_information = df_headers_information[:-2]
    for i, row in df_headers_information.iterrows():
        if row["prediction"] in ["p", "w", "i", "t"]:
            if not i + 1 == len(df_headers_information):
                if row["prediction"] == "p":
                    categories_range["p"].append((df_headers_information.iloc[i]["indexes"], df_headers_information.iloc[i + 1]["indexes"]))
                elif row["prediction"] == "i":
                    categories_range["i"].append((df_headers_information.iloc[i]["indexes"], df_headers_information.iloc[i + 1]["indexes"]))
                elif row["prediction"] == "w":
                    categories_range["w"].append((df_headers_information.iloc[i]["indexes"], df_headers_information.iloc[i + 1]["indexes"]))
                else:
                    categories_range["t"].append((df_headers_information.iloc[i]["indexes"], df_headers_information.iloc[i + 1]["indexes"]))
            else:
                if row["prediction"] == "p":
                    categories_range["p"].append((df_headers_information.iloc[i]["indexes"], len_df_original_text-1))
                elif row["prediction"] == "i":
                    categories_range["i"].append((df_headers_information.iloc[i]["indexes"], len_df_original_text - 1))
                elif row["prediction"] == "w":
                    categories_range["w"].append((df_headers_information.iloc[i]["indexes"], len_df_original_text - 1))
                else:
                    categories_range["t"].append((df_headers_information.iloc[i]["indexes"], len_df_original_text-1))
    return categories_range

def get_paragraphs(original_text_df, ranges):
    paragraphs = []
    for item in ranges:
        paragraphs.append(" ".join(original_text_df[item[0]: item[1]].values))
    services_string = " ".join(paragraph for paragraph in paragraphs)
    return services_string
