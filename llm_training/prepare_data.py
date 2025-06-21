from pathlib import Path
import re
import polars as pl
import matplotlib.pyplot as plt

MD_HEADER_SPLIT = re.compile(r"^#+\ ",re.MULTILINE)
REFERENCE_MATCHES = ["References", "REFERENCES","R E F E R E N C E S", "Re F E R E N C E S"]


dataset = Path("~/data/dataset/v1/notes.zstd.parquet")
df = pl.read_parquet(dataset)
print(f"loaded df: {df.shape}")

# Split md text into main and appendix
def get_main_text(text: str):
    sections = re.split(MD_HEADER_SPLIT, text)
    reference_sections = [i for i, section in enumerate(sections) if any(reference_match in section for reference_match in REFERENCE_MATCHES)]
    if not reference_sections:
        print("no reference section found") # TODO: handle this case better?
        return text, ""
        # print(text)
        # raise ValueError("no reference section found")
    reference_section_index = reference_sections[0]
    reference_section_text = sections[reference_section_index]

    main_text = text.split(reference_section_text)[0] + reference_section_text
    appendix = ''.join(text.split(reference_section_text)[1:])
    return main_text, appendix

texts = df.select(pl.col("pdf_md")).to_series().to_list()
main_texts, appendix_texts = zip(*map(get_main_text, texts))
df = df.with_columns(pl.Series(name="pdf_md_main_text", values=main_texts))
df = df.with_columns(pl.Series(name="pdf_md_appendix_text", values=appendix_texts))

# get overview of main text length distribution
main_text_lengths = df.select(pl.col("pdf_md_main_text").str.len_chars())
fig = main_text_lengths.to_pandas().plot.hist(bins=100)
fig.set_xlabel("Paper length (chars)")
fig.set_ylabel("Number of papers")
plt.tight_layout()
plt.show()
print(main_text_lengths.describe())
# mean: ~50k chars

# Filter based on paper length
min_main_text_length = df.select(pl.col("pdf_md_main_text").str.len_chars()).quantile(.01).item()
max_main_text_length = df.select(pl.col("pdf_md_main_text").str.len_chars()).quantile(.99).item()
print(f"Min main text length: {min_main_text_length}\nMax main text length: {max_main_text_length}")
df = df.filter((pl.col("pdf_md_main_text").str.len_chars() > min_main_text_length) & (pl.col("pdf_md_main_text").str.len_chars() < max_main_text_length))
print(f"filtered paper length: {df.shape}")

# Filter based on review length
df = df.explode('reviews')
df = df.rename({'reviews': 'review'})
df = df.with_columns(review_length=pl.col("review").struct.field("content").list.join('\n').str.len_chars())
print(f"reviews: {df.shape}")

# get overview of review length distribution
review_lengths = df.select(pl.col("review_length"))
fig = review_lengths.to_pandas().plot.hist(bins=100)
fig.set_xlabel("Review length (chars)")
fig.set_ylabel("Number of reviews")
plt.tight_layout()
plt.show()
print(review_lengths.describe())
# mean: ~3.1k chars

min_review_length = df.select(pl.col("review_length")).quantile(.01).item()
max_review_length = df.select(pl.col("review_length")).quantile(.99).item()
print(f"Min review length: {min_review_length}\nMax review length: {max_review_length}")
df = df.filter((pl.col("review").struct.field("content").list.join('\n').str.len_chars() > min_review_length) & (pl.col("review").struct.field("content").list.join('\n').str.len_chars() < max_review_length))
print(df.shape)
print(f"filtered review length: {df.shape}")



# filter based on reviewer confidence
def filter_confident_reviews(row):
    review = row['review']
    confidence_index = review['content_fields'].index('confidence')
    confidence_value = review['content'][confidence_index]
    match row['or_venue']:
        case 'ICLR.cc/2022/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'ICLR.cc/2023/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'ICLR.cc/2024/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'ICLR.cc/2025/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'NeurIPS.cc/2022/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'NeurIPS.cc/2023/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case 'NeurIPS.cc/2024/Conference':
            confidence_value = int(confidence_value[0])
            return confidence_value >= 4
        case _:
            raise ValueError(f"Unknown venue: {row['or_venue']}")
            # return True

keep = []
for row in df.select('review', 'or_venue').rows(named=True):
    if filter_confident_reviews(row):
        keep.append(True)
    else:
        keep.append(False)
df = df.with_columns(pl.Series(name="confidence_filter", values=keep))
df = df.filter(pl.col("confidence_filter"))
print(f"filtered review confidence: {df.shape}")

# # format reviews
dataset = []
for row in df.rows(named=True):
    paper_text = row["pdf_md_main_text"]
    review_content_fields = row["review"]["content_fields"]
    review_content = row["review"]["content"]
    review_content_meta = row["review"]["content_meta"]

    review_fields = '\n'.join([f"## {field.replace('_', ' ').title()}\n{field_description}\n" for field, field_description in zip(review_content_fields, review_content_meta)])
    review = '# Review\n\n' + '\n'.join([f"## {field.replace('_', ' ').title()}\n{content}\n" for field, content in zip(review_content_fields, review_content)])
    dataset.append({'paper_text': paper_text, 'review_fields': review_fields, 'review': review, 'or_venue': row['or_venue'], 'id': row['id']})

dataset_df = pl.from_dicts(dataset)

test_set_ids = []
test_set_ids.extend(dataset_df.filter(pl.col('or_venue') == 'ICLR.cc/2025/Conference').select(pl.col('id').unique()).sample(fraction=1.0).head(200).select('id').to_series().to_list())
test_set_ids.extend(dataset_df.filter(pl.col('or_venue') == 'NeurIPS.cc/2024/Conference').select(pl.col('id').unique()).sample(fraction=1.0).head(200).select('id').to_series().to_list())

df_train = dataset_df.filter(~pl.col('id').is_in(test_set_ids))
df_test = dataset_df.filter(pl.col('id').is_in(test_set_ids))


dataset_df.write_parquet("data/dataset.zstd.parquet")
df_train.write_parquet("data/dataset_train.zstd.parquet")
# df_test.write_parquet("dataset_test.zstd.parquet")


# prepare test set for generation
df_test = df_test.unique(subset=(pl.col("id"), pl.col("paper_text"), pl.col("review_fields"), pl.col("or_venue"))).join(df_test.select(pl.col('id'), pl.col('review')).group_by('id').agg(pl.col('review').alias('reviews')), on='id', how='left')
df_test.write_parquet("data/dataset_test.zstd.parquet")
"""
test dataset schema:
Schema([('paper_text', String),
        ('review_fields', String),
        ('review', String),
        ('or_venue', String),
        ('id', String),
        ('reviews', List(String))])
"""
