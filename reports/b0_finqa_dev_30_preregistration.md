# B0 FinQA development-set 30-item preregistration

- Protocol: `contractfin-b0-finqa-dev30-v1`
- Registration date: `2026-09-28`
- Dataset SHA-256: `91237413e337148faf0ae58c06539d8c428fbf2f06ef84dc335cdd0616032739`
- Selected items: `30`
- Purpose: coverage-oriented interface and pipeline smoke test; not a performance estimate.
- Frozen rule: no sample substitution and no item-specific prompt/evaluator tuning.

## Registered allocation

| Stratum | Eligible | Selected |
|---|---:|---:|
| `single_divide` | 287 | 5 |
| `single_subtract` | 137 | 4 |
| `single_add` | 30 | 2 |
| `single_multiply` | 25 | 2 |
| `table_average` | 19 | 2 |
| `table_sum` | 4 | 1 |
| `table_max` | 7 | 1 |
| `table_min` | 5 | 1 |
| `comparison` | 10 | 2 |
| `contains_exp` | 1 | 1 |
| `multi_2_step` | 287 | 4 |
| `multi_3_step` | 41 | 2 |
| `multi_4_step` | 13 | 1 |
| `multi_5_step` | 16 | 2 |

## Frozen execution list

Gold answers and full gold programs are deliberately omitted from this review file.

| Order | Sample ID | Stratum | Steps | Evidence | Question |
|---:|---|---|---:|---:|---|
| 1 | `finqa:dev:LMT/2010/page_42.pdf-2` | `single_divide` | 1 | 2 | what is the percentage increase in the net cash provided by operating activities in 2010 compare to 2009? |
| 2 | `finqa:dev:SYY/2019/page_9.pdf-1` | `single_subtract` | 1 | 1 | what was the change in the percentage of sales to restaurants from 2017 to 2018? |
| 3 | `finqa:dev:JPM/2014/page_65.pdf-4` | `comparison` | 1 | 2 | did jpmorgan chase outperform the s&p 500 over the five year period? |
| 4 | `finqa:dev:JPM/2018/page_110.pdf-1` | `multi_3_step` | 3 | 1 | what is the average of the afs investment securities during the years 2016-2018? |
| 5 | `finqa:dev:JKHY/2014/page_30.pdf-1` | `single_subtract` | 1 | 1 | what was the cumulative total return on the s & p 500 for the five year period? |
| 6 | `finqa:dev:AWK/2013/page_132.pdf-4` | `single_add` | 1 | 1 | what was the net effect of the one-percentage point increase and decrease on total service and interest cost components |
| 7 | `finqa:dev:JPM/2007/page_147.pdf-1` | `single_add` | 1 | 2 | in 2007 what was the percent of the retained interest of the total principal amount of beneficial interests |
| 8 | `finqa:dev:RE/2015/page_33.pdf-3` | `single_multiply` | 1 | 1 | what is the total value of fixed maturities and cash as of december 31 , 2015 , in billions? |
| 9 | `finqa:dev:PPG/2011/page_70.pdf-2` | `multi_3_step` | 3 | 2 | what was the increase for the maximum company match on january 1 , 2011? |
| 10 | `finqa:dev:CB/2010/page_200.pdf-4` | `single_divide` | 1 | 2 | in 2010 what was the ratio of the statutory capital and surplus to the statutory net income |
| 11 | `finqa:dev:AON/2009/page_46.pdf-2` | `table_min` | 1 | 1 | what is the lowest segment operating income? |
| 12 | `finqa:dev:PPG/2013/page_40.pdf-1` | `comparison` | 1 | 2 | does the company spend more on advertising in 2013 than on research and development? |
| 13 | `finqa:dev:LMT/2012/page_47.pdf-3` | `multi_2_step` | 2 | 1 | what is the growth rate in operating profit for space systems in 2011? |
| 14 | `finqa:dev:AON/2014/page_47.pdf-1` | `table_average` | 3 | 1 | what is the variation between the average and the highest operating margin? |
| 15 | `finqa:dev:AAPL/2014/page_38.pdf-1` | `table_max` | 1 | 1 | in what year was the cash cash equivalents and marketable securities the highest? |
| 16 | `finqa:dev:AMAT/2014/page_18.pdf-1` | `multi_4_step` | 4 | 1 | what is the growth rate in sales from 2013 to 2014? |
| 17 | `finqa:dev:AAPL/2008/page_78.pdf-2` | `table_average` | 1 | 1 | what was the average change in unrealized gains on derivative instruments? |
| 18 | `finqa:dev:ABMD/2006/page_75.pdf-3` | `single_divide` | 1 | 2 | what percentage of total future minimum lease payments are due in 2008? |
| 19 | `finqa:dev:SWKS/2006/page_81.pdf-2` | `single_divide` | 1 | 2 | what is the percentage change in in the pension liability balance from 2004 to 2006? |
| 20 | `finqa:dev:BKR/2017/page_103.pdf-4` | `single_multiply` | 1 | 1 | what is the total value of rsus converted to bhge rsus , in millions? |
| 21 | `finqa:dev:MRO/2004/page_36.pdf-2` | `table_sum` | 1 | 1 | what were total heavy fuel oil sales in tbd for the three year period? |
| 22 | `finqa:dev:ZBH/2003/page_58.pdf-2` | `single_subtract` | 1 | 1 | what is the change in finished goods in millions between 2002 and 2003? |
| 23 | `finqa:dev:IP/2006/page_32.pdf-2` | `single_divide` | 1 | 2 | in 2005 what percentage of consumer packaging sales were represented by foodservice net sales? |
| 24 | `finqa:dev:C/2017/page_328.pdf-3` | `multi_5_step` | 5 | 2 | what was the difference in percentage cumulative total return for the five year period ended 31-dec-2017 of citi common stock and s&p financials? |
| 25 | `finqa:dev:APD/2018/page_59.pdf-1` | `contains_exp` | 4 | 2 | considering the fair market value of plan assets in 2018 , what is its estimated return for 10 years? |
| 26 | `finqa:dev:OKE/2008/page_86.pdf-2` | `multi_2_step` | 2 | 2 | what was the percentage change in net fair value of derivatives outstanding at between 2007 and 2008 in thousands? |
| 27 | `finqa:dev:PNC/2011/page_78.pdf-3` | `single_subtract` | 1 | 1 | between december 31 , 2011 and december 31 , 2010 , what was the change in the unpaid principal balance outstanding of loans sold as a participant in these programs in billions? |
| 28 | `finqa:dev:LKQ/2016/page_26.pdf-2` | `multi_5_step` | 5 | 2 | what was the difference in percentage cumulative return for lkq corporation and the s&p 500 index for the five years ended 12/31/2016? |
| 29 | `finqa:dev:SNPS/2006/page_69.pdf-2` | `multi_2_step` | 2 | 2 | what percentage of the total purchase price is represented by goodwill? |
| 30 | `finqa:dev:PNC/2011/page_78.pdf-1` | `multi_2_step` | 2 | 1 | for december 31 , 2011 and december 31 , 2010 , what was the average unpaid principal balance outstanding of loans sold as a participant in these programs , in billions? |

## Prior gate exclusion

| Sample ID | Source position | Reason |
|---|---:|---|
| `finqa:dev:V/2008/page_17.pdf-1` | 1 | Used for the authorized one-item DeepSeek interface gate before preregistration. |
