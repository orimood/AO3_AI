---
annotations_creators:
- found
language:
- ar
- bg
- ca
- cs
- da
- de
- el
- en
- es
- et
- fa
- fi
- fr
- he
- hi
- hr
- hu
- id
- it
- ja
- ko
- lt
- lv
- ms
- nl
- no
- pl
- pt
- ro
- ru
- sk
- sl
- sr
- sv
- th
- tr
- uk
- vi
- zh
language_bcp47:
- pt-BR
- zh-HK
- zh-TW
multilinguality:
- multilingual
size_categories:
- 10M<n<100M
source_datasets:
- original
task_categories:
- text-generation
- text-classification
task_ids:
- language-modeling
- topic-classification
configs:
  - config_name: train
    data_files:
      - split: train
        path: '*.jsonl.zst'
    default: true
---
# Dataset Card for AO3
### Dataset Summary
This dataset contains approximately 12.6 million publicly available works from AO3. The dataset was created by processing works with IDs from 1 to 63,200,000 that are publicly accessible. Each entry contains the full text of the work along with comprehensive metadata including title, author, fandom, relationships, characters, tags, warnings, and other classification information.

### Languages
The dataset is multilingual, with works in many different languages, though English is predominant.

## Dataset Structure
### Data Files
The dataset is stored in compressed JSONL files (jsonl.zst format), with each archive containing 100,000 sequential IDs. For example, `ao3_40500001-40600000.jsonl.zst` contains works with IDs in that range.

### Data Fields
This dataset includes the following fields:
- `id`: Unique identifier for the work (string)
- `title`: Title of the work (string)
- `metadata`: Dictionary containing:
  - `Archive Warning`: Content warnings for the work
  - `Category`: Relationship categories (e.g., F/M, M/M, F/F)
  - `Characters`: List of characters appearing in the work
  - `Fandom`: Fandom(s) the work belongs to
  - `Language`: Language of the work
  - `Rating`: Content rating (e.g., General Audiences, Teen And Up, Mature, Explicit)
  - `Relationship`: Specific relationship pairings featured
  - `Series`: Series the work belongs to, if applicable
  - `author`: Username of the creator
  - `chapters`: Chapter structure information (e.g., "1/1" for a completed one-shot)
  - `completed`: Whether the work is completed
  - `published`: Publication date
  - `words`: Word count
- `text`: Main content of the work (string)

### Data Splits
All examples are in a single split.
