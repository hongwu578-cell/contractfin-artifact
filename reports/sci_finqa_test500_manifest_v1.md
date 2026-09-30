# FinQA held-out 500-item manifest

- Protocol: `contractfin-sci-finqa-test500-v1`
- Registration date: `2026-09-29`
- Source test SHA-256: `da64fbde6763d0832a04c4f17e7a945bb3f195ab23e12bc57b31167a5b745541`
- Primary items: `500`
- Stability items: `100`
- Substitution: prohibited
- Gold answers and programs are intentionally omitted from this review document.

## Frozen allocation

| Stratum | Eligible | Minimum | Final |
|---|---:|---:|---:|
| `comparison` | 20 | 10 | 14 |
| `contains_exp` | 3 | 3 | 3 |
| `multi_2_step` | 407 | 0 | 166 |
| `multi_3_step` | 55 | 0 | 22 |
| `multi_4_step` | 10 | 8 | 9 |
| `multi_5_step` | 16 | 10 | 12 |
| `single_add` | 54 | 0 | 22 |
| `single_divide` | 367 | 0 | 149 |
| `single_multiply` | 36 | 0 | 15 |
| `single_subtract` | 140 | 0 | 57 |
| `table_average` | 15 | 8 | 11 |
| `table_max` | 10 | 6 | 8 |
| `table_min` | 4 | 4 | 4 |
| `table_sum` | 10 | 6 | 8 |

## Frozen execution list

| Order | Sample ID | Stratum | Steps | Stability | Question |
|---:|---|---|---:|:---:|---|
| 1 | `finqa:test:DVN/2014/page_87.pdf-3` | `single_divide` | 1 |  | at december 31 , 2014 what was the ratio of the debt maturities scheduled for 2015 to 2018 |
| 2 | `finqa:test:C/2008/page_22.pdf-1` | `multi_2_step` | 2 |  | what was the tax rate applied to the company recorded sales of the mastercard shares in 2007 , the company recorded a $ 367 million after-tax gain ( $ 581 million pretax ) |
| 3 | `finqa:test:AWK/2014/page_121.pdf-4` | `single_divide` | 1 | yes | what was canadian nol's as a percentage of state nol's in 2014? |
| 4 | `finqa:test:MRO/2006/page_93.pdf-2` | `comparison` | 1 | yes | was the fin 47 liability greater on december 31 2004 than december 31 2005? |
| 5 | `finqa:test:CDNS/2018/page_66.pdf-4` | `single_subtract` | 1 |  | what is the net effect of the cumulative effect adjustments , net of income tax effects , to beginning retained earnings for new accounting standards adopted by cadence on the retained earnings balance as adjusted for december 30 , 2017 , in thousands? |
| 6 | `finqa:test:PNC/2012/page_247.pdf-4` | `multi_2_step` | 2 |  | what was the average , in millions , reserve for losses in 2011 and 2012? |
| 7 | `finqa:test:BLK/2017/page_121.pdf-1` | `multi_2_step` | 2 |  | what is the percentage change in the fair value of company's interest in pennymac from 2016 to 2017? |
| 8 | `finqa:test:GS/2015/page_171.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in securities purchased under agreements to resell between 2014 and 2015? |
| 9 | `finqa:test:CDNS/2015/page_30.pdf-3` | `multi_5_step` | 5 | yes | what was the difference in percentage cumulative 5-year total stockholder return for cadence design systems inc . and the nasdaq copmosite for the period ended 1/3/2015? |
| 10 | `finqa:test:CMCSA/2015/page_67.pdf-3` | `single_divide` | 1 |  | what was the percentage of the capital expenditures incurred in our cable communications for customer premise equipment in 2015 |
| 11 | `finqa:test:DRE/2008/page_46.pdf-1` | `single_divide` | 1 |  | what is the net income per common share in 2008? |
| 12 | `finqa:test:BKR/2017/page_56.pdf-2` | `multi_2_step` | 2 |  | what is the cash held on behalf of ge as a percentage of cash and equivalents in 2017? |
| 13 | `finqa:test:SNA/2018/page_31.pdf-1` | `single_divide` | 1 |  | for the quarter ended 12/29/2018 what was the percent of the total shares bought after 11/25/2018 |
| 14 | `finqa:test:CME/2017/page_40.pdf-1` | `contains_exp` | 5 |  | what is the anualized return for cme group from 2012 to 2017? |
| 15 | `finqa:test:HIG/2004/page_140.pdf-1` | `single_divide` | 1 |  | in the adoption of the prospective method what was the ratio of the other comprehensive income to the net income reclassifying certain separate accounts to general account |
| 16 | `finqa:test:IP/2006/page_75.pdf-2` | `single_divide` | 1 | yes | at december 31 , 2006 , what percentage of total future minimum commitments under existing non-cancelable leases and purchase obligations from lease obligations is due in 2008? |
| 17 | `finqa:test:PNC/2012/page_100.pdf-3` | `single_add` | 1 |  | how many total private investor repurchase claims were there in 2011 and 2012 combined , in millions? |
| 18 | `finqa:test:UPS/2012/page_32.pdf-3` | `multi_2_step` | 2 |  | what is the roi of an investment in s&p500 from 2008 to 2009? |
| 19 | `finqa:test:AES/2001/page_85.pdf-2` | `multi_2_step` | 2 |  | prior to the first remarketing date , what is the annual interest cost on the remarketable or redeemable securities ( 2018 2018roars 2019 2019 ) ? |
| 20 | `finqa:test:DISH/2011/page_122.pdf-4` | `multi_2_step` | 2 |  | for the terrestar acquisition what will the final cash purchase price be in millions paid upon closing? |
| 21 | `finqa:test:ABMD/2007/page_78.pdf-1` | `table_average` | 1 |  | what is the average expected volatility used in the black scholes formula? |
| 22 | `finqa:test:HOLX/2009/page_127.pdf-2` | `single_divide` | 1 | yes | what portion of the total estimated purchase price is paid in cash? |
| 23 | `finqa:test:ETFC/2007/page_18.pdf-1` | `single_divide` | 1 |  | as of december 2007 what was the ratio of the square footage in alpharetta georgia to charlotte north carolina |
| 24 | `finqa:test:AMT/2006/page_104.pdf-2` | `multi_2_step` | 2 |  | what portion of the ati 7.25% ( 7.25 % ) notes was paid off during 2006? |
| 25 | `finqa:test:BLL/2010/page_37.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in cash flows provided by ( used in ) operating activities including discontinued operations between 2009 and 2010? |
| 26 | `finqa:test:MRO/2006/page_93.pdf-1` | `multi_2_step` | 2 |  | by what percentage did total amount of the liability for asset retirement obligations increase from 2003 to 2005? |
| 27 | `finqa:test:GS/2014/page_74.pdf-1` | `single_divide` | 1 |  | in 2013 what percentage of gcla is in non-u.s . dollar denominated assets? |
| 28 | `finqa:test:ADI/2010/page_80.pdf-1` | `multi_2_step` | 2 | yes | what is the growth rate in the balance of money market funds in 2010? |
| 29 | `finqa:test:IP/2006/page_30.pdf-1` | `single_divide` | 1 |  | brazilian paper sales represented what percentage of printing papers in 2006? |
| 30 | `finqa:test:AAPL/2003/page_48.pdf-2` | `single_subtract` | 1 | yes | what was the net change in millions of asset retirement liability in the year ended september 27 2003? |
| 31 | `finqa:test:GS/2018/page_69.pdf-4` | `table_max` | 1 | yes | in millions for the years 2018 , 2017 , 2016 , what was the largest provision for credit losses? |
| 32 | `finqa:test:HWM/2018/page_96.pdf-1` | `single_multiply` | 1 |  | considering the average exercise price of options , what is the estimated total value of stock options in 2018 , in millions of dollars? |
| 33 | `finqa:test:CE/2016/page_19.pdf-1` | `multi_2_step` | 2 |  | what is the total research and development for the year 2014 through 2016 in millions |
| 34 | `finqa:test:ECL/2017/page_94.pdf-2` | `single_subtract` | 1 |  | what is the difference between the statutory u.s . rate and the effective income tax rate in 2016? |
| 35 | `finqa:test:UNP/2011/page_24.pdf-4` | `multi_2_step` | 2 |  | what was the percentage change in free cash flow from 2001 to 2011? |
| 36 | `finqa:test:PPG/2012/page_29.pdf-2` | `single_divide` | 1 | yes | what was the average cost per share for the share repurchases in 2012? |
| 37 | `finqa:test:CE/2016/page_19.pdf-4` | `multi_3_step` | 3 |  | what was the percentage change in the the research and development costs from 2014 to 2015 |
| 38 | `finqa:test:LKQ/2016/page_87.pdf-4` | `single_divide` | 1 |  | in 2016 what was the percent of the total future minimum lease commitments due in 2019 |
| 39 | `finqa:test:CB/2010/page_83.pdf-1` | `single_subtract` | 1 |  | what is the change in fair value of financial market instruments as part of the hedging strategy during 2010? |
| 40 | `finqa:test:MKTX/2004/page_99.pdf-2` | `multi_2_step` | 2 | yes | as of december 31 , 2004 , what percentage of common stock outstanding were non-voting shares? |
| 41 | `finqa:test:LMT/2012/page_73.pdf-2` | `multi_2_step` | 2 |  | what was the percent of the change in weighted average common shares outstanding for diluted computations from 2011 to 2012 |
| 42 | `finqa:test:MS/2007/page_179.pdf-2` | `single_divide` | 1 |  | what percentage of net assets acquired is amortizable intangible assets? |
| 43 | `finqa:test:ETR/2016/page_23.pdf-4` | `single_subtract` | 1 |  | assuming there would not have been a sale of the 583 mw rhode island state energy center in 2015 . what would have net revenue be without this gain on sale? |
| 44 | `finqa:test:SLG/2001/page_48.pdf-3` | `multi_3_step` | 3 | yes | what was the average total revenue in 1999 , 2000 and 2001? |
| 45 | `finqa:test:PNC/2012/page_68.pdf-5` | `single_divide` | 1 | yes | commercial mortgage loans held for sale designated at fair value at december 31 , 2012 were what percent of total loans held for sale?, |
| 46 | `finqa:test:JPM/2010/page_281.pdf-1` | `single_divide` | 1 |  | what was the percent of the firm 2019s total pledged assets in 2010 that was loans |
| 47 | `finqa:test:AON/2007/page_171.pdf-3` | `table_average` | 1 | yes | what are the average net unrealized investment gains for the period? |
| 48 | `finqa:test:PNC/2012/page_247.pdf-2` | `multi_2_step` | 2 |  | for 2011 and 2012 , what were average commercial mortgage recourse obligations in millions? |
| 49 | `finqa:test:MRO/2008/page_45.pdf-2` | `single_divide` | 1 |  | what percentage of pipeline barrels handled consisted of crude oil trunk lines in 2007? |
| 50 | `finqa:test:CMCSA/2015/page_67.pdf-1` | `single_divide` | 1 | yes | what was the percentage cable distribution systems capital expenditures of the capital expenditures incurred in cable communications segment capital expenditures in 2015? |
| 51 | `finqa:test:ETR/2008/page_298.pdf-4` | `multi_2_step` | 2 |  | what is the percent change in receivables from the money pool between 2007 and 2008? |
| 52 | `finqa:test:MRO/2013/page_39.pdf-3` | `multi_2_step` | 2 |  | by what percentage did the average price of wti crude oil increase from 2011 to 2013? |
| 53 | `finqa:test:DVN/2018/page_35.pdf-4` | `multi_2_step` | 2 |  | what was the tax rate on the net earnings due to the gain on the sale of our aggregate ownership interests in enlink discontinued operations |
| 54 | `finqa:test:MSI/2007/page_70.pdf-3` | `multi_4_step` | 4 | yes | what was the growth of consolidated net sales , in percentage , from 2005 to 2007 |
| 55 | `finqa:test:ETR/2011/page_301.pdf-1` | `multi_2_step` | 2 |  | what is the percentage decrease in receivables from the money pool from 2010 to 2011? |
| 56 | `finqa:test:AON/2007/page_175.pdf-2` | `multi_2_step` | 2 | yes | what is the net change in aon 2019s unpaid restructuring liabilities during 2006? |
| 57 | `finqa:test:MRO/2013/page_19.pdf-1` | `table_sum` | 1 | yes | what was total acres expiring in millions for other africa? |
| 58 | `finqa:test:AMT/2006/page_104.pdf-1` | `single_divide` | 1 |  | as of december 31 , 2006 , what was the total total cash obligations aggregate carrying value of long-term debt due in 2006 |
| 59 | `finqa:test:HWM/2017/page_42.pdf-2` | `contains_exp` | 5 | yes | what is the annualized return for the s&p 500 aematerials index during 2012 and 2017? |
| 60 | `finqa:test:MRO/2013/page_19.pdf-2` | `multi_2_step` | 2 |  | by how much did net undeveloped acres expiring decrease from 2015 to 2016? |
| 61 | `finqa:test:SLB/2012/page_56.pdf-1` | `single_subtract` | 1 |  | what would the 2012 shares outstanding in millions have been without the acquisition of smith international? |
| 62 | `finqa:test:DISH/2011/page_122.pdf-1` | `single_subtract` | 1 |  | what is the working capital of blockbuster at the point of acquisition? |
| 63 | `finqa:test:IP/2006/page_30.pdf-3` | `single_divide` | 1 |  | what was the profit margin of printing papers in 2005 |
| 64 | `finqa:test:DG/2005/page_44.pdf-3` | `single_add` | 1 | yes | what is the cost difference over lifo in the last two years? |
| 65 | `finqa:test:MRO/2003/page_45.pdf-1` | `table_sum` | 1 |  | what were total asphalt sales in millions for the three year period? |
| 66 | `finqa:test:MRO/2004/page_46.pdf-2` | `single_add` | 1 | yes | how many total shares were repurchase in the periods 11/01/04 2013 11/30/04 and \\n12/01/04 2013 12/31/04? |
| 67 | `finqa:test:FIS/2016/page_31.pdf-2` | `multi_5_step` | 5 |  | what was the difference in percentage cumulative 5-year total shareholder return on common stock fidelity national information services , inc . compared to the s&p 500 for the period ending 12/16? |
| 68 | `finqa:test:ILMN/2008/page_86.pdf-3` | `single_divide` | 1 | yes | what was the percentage change in the uncertain tax positions from 2007 to 2008? |
| 69 | `finqa:test:MSI/2012/page_87.pdf-1` | `multi_3_step` | 3 |  | what was the average expected volatility of the weighted-average estimated fair value of employee stock options from 2010 to 2012 |
| 70 | `finqa:test:ABMD/2012/page_41.pdf-2` | `comparison` | 1 | yes | did abiomed outperform the nasdaq medical equipment index? |
| 71 | `finqa:test:AAPL/2006/page_100.pdf-4` | `table_min` | 1 | yes | what was the lowest effective tax rate in the three year period? |
| 72 | `finqa:test:UNP/2011/page_24.pdf-1` | `comparison` | 1 | yes | in 2012 , are the planned capital expenditures greater than free cash flow in 2011? |
| 73 | `finqa:test:STT/2007/page_111.pdf-1` | `multi_2_step` | 2 |  | what is the percentage change in the the balance of cash and u.s . government securities from 2006 to 2007? |
| 74 | `finqa:test:APD/2016/page_40.pdf-1` | `single_subtract` | 1 | yes | what is the increase in the operating margin observed in 2015 and 2016? |
| 75 | `finqa:test:AAL/2015/page_114.pdf-2` | `single_divide` | 1 |  | what is the percent of the professional fees as part of the total re-organization costs |
| 76 | `finqa:test:SYY/2006/page_71.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in total rental expense under operating leases from july 2 , 2005 to july 1 , 2006? |
| 77 | `finqa:test:ETR/2016/page_23.pdf-1` | `multi_2_step` | 2 | yes | what is the growth rate in net revenue in 2015 for entergy corporation? |
| 78 | `finqa:test:UAA/2016/page_42.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in inventories from 2015 to 2016? |
| 79 | `finqa:test:CDW/2015/page_93.pdf-2` | `multi_3_step` | 3 |  | how much more money was expensed per outstanding basic weighted-average share in the year ended dec 31 , 2013 compared to the year ended dec 31 , 2014? |
| 80 | `finqa:test:IPG/2006/page_77.pdf-4` | `multi_2_step` | 2 |  | what percent increase in long-term debt did the floating rate notes maturing in 2010? |
| 81 | `finqa:test:AES/2001/page_85.pdf-4` | `single_divide` | 1 |  | what percentage of scheduled maturities of total debt at december 31 , 2001 are due in 2005? |
| 82 | `finqa:test:LMT/2014/page_77.pdf-2` | `single_subtract` | 1 |  | what was the change in millions of the weighted average common shares outstanding for diluted computations from 2013 to 2014? |
| 83 | `finqa:test:GS/2018/page_69.pdf-3` | `multi_2_step` | 2 |  | what is the total net revenues in the consolidated statements of earnings in 2016? |
| 84 | `finqa:test:HWM/2015/page_173.pdf-2` | `multi_5_step` | 5 | yes | what was the increase in the settlements with tax authorities as a percent of the tax liabilities observed during 2013 and 2014? |
| 85 | `finqa:test:UNP/2011/page_33.pdf-1` | `multi_2_step` | 2 |  | with a similar improvement as in 2010 , what would expected operating ratio be in 2011? |
| 86 | `finqa:test:FIS/2012/page_48.pdf-4` | `single_subtract` | 1 |  | what is the unfavorable impact in the operating expense in 2012 resulting from a stronger u.s . dollar? |
| 87 | `finqa:test:UNP/2015/page_56.pdf-1` | `single_divide` | 1 |  | in 2015 what was the percent of the total operating revenues associated with agriculture products |
| 88 | `finqa:test:ADI/2010/page_80.pdf-3` | `multi_2_step` | 2 | yes | based on the table , what would be the annual percent return for the companies investments? |
| 89 | `finqa:test:RSG/2009/page_140.pdf-2` | `multi_2_step` | 2 | yes | what was the percentage decline in the weighted- average estimated fair values of stock options from 2007 to 2008 |
| 90 | `finqa:test:BDX/2018/page_106.pdf-3` | `multi_3_step` | 3 | yes | what is the average of total other income from 2016-2018 , in millions? |
| 91 | `finqa:test:AMT/2008/page_94.pdf-2` | `single_subtract` | 1 | yes | what will be the balance of aggregate carrying value of long-term debt as of december 31 , 2009? |
| 92 | `finqa:test:MRO/2003/page_84.pdf-4` | `table_average` | 1 |  | for 2002 and 2003 , what is the average crack spread values? |
| 93 | `finqa:test:ADBE/2008/page_89.pdf-2` | `multi_2_step` | 2 | yes | what is the percentage change in the the gross liability for unrecognized tax benefits during 2008 compare to 2007? |
| 94 | `finqa:test:MRO/2017/page_96.pdf-3` | `table_average` | 1 |  | what was the average initial health care trend rate for the three year period in%? |
| 95 | `finqa:test:NKE/2009/page_43.pdf-1` | `single_add` | 1 |  | what is the total amount , in millions of dollars , outstanding in 2009? |
| 96 | `finqa:test:FIS/2016/page_31.pdf-3` | `multi_3_step` | 3 |  | what is the total return if $ 100000 are invested in s&p500 in 12/11 and sold in 12/16? |
| 97 | `finqa:test:GIS/2018/page_110.pdf-1` | `single_add` | 1 |  | what is the total value of issued guarantees and comfort letters for consolidated subsidiaries and non-consolidated affiliates , ( in millions ) ? |
| 98 | `finqa:test:TMUS/2017/page_29.pdf-3` | `single_divide` | 1 |  | what is the approximate size of each data center leased in square feet |
| 99 | `finqa:test:AAL/2016/page_8.pdf-3` | `single_divide` | 1 | yes | what is the percent of the passenger service personnel as a part of the total number of personnel |
| 100 | `finqa:test:MRO/2011/page_108.pdf-2` | `table_sum` | 1 |  | what were total development costs in millions for the three year period? |
| 101 | `finqa:test:ADI/2011/page_61.pdf-2` | `multi_2_step` | 2 |  | what is the percentage change in cash flow hedges in 2011 compare to the 2010? |
| 102 | `finqa:test:ANSS/2016/page_47.pdf-1` | `single_divide` | 1 | yes | as of december 31 , 2016 what was the percent of the company's significant contractual obligations for the global headquarters operating lease due in 2016 |
| 103 | `finqa:test:BLL/2012/page_31.pdf-4` | `single_subtract` | 1 |  | the five year total return for the period ending 12/31/2012 on ball corporation stock was how much greater than the same return on the dj us containers & packaging index? |
| 104 | `finqa:test:ETR/2015/page_17.pdf-2` | `multi_2_step` | 2 |  | what is the growth rate of net revenue from 2014 to 2015 ? |
| 105 | `finqa:test:CME/2017/page_89.pdf-3` | `single_divide` | 1 |  | based on the effective tax rate , what is the gross amount of the recognized tax benefit the year ended december 31 , 2017 in billions?? |
| 106 | `finqa:test:AON/2007/page_171.pdf-4` | `multi_2_step` | 2 |  | what is the percentual increase observed in the net derivative gains during 2006 and 2007? |
| 107 | `finqa:test:RSG/2012/page_93.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in the additions charged to expense from 2011 to 2012 as part of the allowance for doubtful accounts |
| 108 | `finqa:test:C/2009/page_243.pdf-1` | `single_divide` | 1 |  | what was the ratio of the net increase in the in securities sold under agreements to repurchase to the net transfers in |
| 109 | `finqa:test:MRO/2006/page_93.pdf-4` | `single_add` | 1 |  | as of december 31 , 2005 , what was the before tax charge related to adopting fin no . 47 in millions? |
| 110 | `finqa:test:DVN/2014/page_87.pdf-1` | `multi_3_step` | 3 |  | what percentage increase occurred from oct 24 , 2017 to oct 24 , 2018 of senior credit facility maturity? |
| 111 | `finqa:test:UNP/2007/page_25.pdf-3` | `single_subtract` | 1 |  | what was change in millions of free cash flow from 2005 to 2007? |
| 112 | `finqa:test:ETR/2016/page_150.pdf-3` | `multi_4_step` | 4 |  | what is the total expected payments on the bonds for the next 5 years for entergy new orleans storm recovery funding? |
| 113 | `finqa:test:DVN/2012/page_77.pdf-1` | `multi_2_step` | 2 |  | what percentage of debt matured between 2016 and 2017? |
| 114 | `finqa:test:LMT/2016/page_49.pdf-3` | `table_average` | 1 |  | what were average net sales for mfc in millions between 2014 and 2016? |
| 115 | `finqa:test:RCL/2012/page_75.pdf-1` | `single_divide` | 1 |  | assuming each continent has the same number of destinations , approximately how many destinations does each continent have? |
| 116 | `finqa:test:ECL/2017/page_79.pdf-2` | `single_divide` | 1 |  | what portion of anios' purchasing price is related to goodwill? |
| 117 | `finqa:test:C/2009/page_45.pdf-2` | `single_divide` | 1 |  | what percent of net interest revenue where total operating expenses in 2008? |
| 118 | `finqa:test:ETR/2011/page_17.pdf-2` | `multi_2_step` | 2 |  | what is the total amount of variance that favorably affected net revenue in 2011? |
| 119 | `finqa:test:C/2009/page_63.pdf-1` | `single_divide` | 1 |  | in 2010 what was the ratio of the non-us pension plans , discretionary contributions to the postretirement benefit plans |
| 120 | `finqa:test:RSG/2016/page_145.pdf-1` | `single_divide` | 1 |  | what was the ratio of the tons hedged in 2017 to 2018 |
| 121 | `finqa:test:GS/2017/page_132.pdf-2` | `table_min` | 1 |  | in millions for 2017 and 2016 , what was the minimum balance of cash instruments? |
| 122 | `finqa:test:PPG/2012/page_29.pdf-1` | `multi_2_step` | 2 |  | what are cumulative three year dividends in millions? |
| 123 | `finqa:test:HOLX/2006/page_71.pdf-1` | `single_multiply` | 1 |  | what would the cash impact be if all outstanding options warrants and rights were exercised? |
| 124 | `finqa:test:DISCA/2014/page_64.pdf-3` | `comparison` | 1 |  | after 4 years , did the series c outperform the s&p 500? |
| 125 | `finqa:test:GS/2014/page_51.pdf-2` | `multi_2_step` | 2 |  | what is the percentage change in inventory balance in 2014? |
| 126 | `finqa:test:GS/2012/page_189.pdf-1` | `table_max` | 1 |  | in millions for 2012 and 2011 , what was the largest tier 1 capital amount?\\n |
| 127 | `finqa:test:VRTX/2006/page_111.pdf-2` | `single_divide` | 1 |  | what percent of the gross total property and equipment values in 2006 are related to computers? |
| 128 | `finqa:test:TFX/2017/page_78.pdf-3` | `single_multiply` | 1 |  | if the remaining securities would be use or exercised at $ 113.49 , what would cost be for the company? |
| 129 | `finqa:test:CDNS/2015/page_30.pdf-1` | `multi_2_step` | 2 |  | what is the rate of return in nasdaq of an investment from 2010 to 2011? |
| 130 | `finqa:test:ABMD/2012/page_41.pdf-1` | `comparison` | 1 |  | did abiomed outperform the nasdaq composite index? |
| 131 | `finqa:test:CME/2017/page_89.pdf-2` | `single_subtract` | 1 |  | what was the decrease of the effective tax expense rate between 2015 and 2016? |
| 132 | `finqa:test:BKNG/2016/page_33.pdf-1` | `single_divide` | 1 | yes | at the measurement point december 312016 what was the ratio of the the priceline group inc . . to the nasdaqcomposite index |
| 133 | `finqa:test:SLG/2011/page_91.pdf-5` | `single_divide` | 1 | yes | what percentage of the beginning balance of 2010 was vested during the year? |
| 134 | `finqa:test:AWK/2013/page_122.pdf-2` | `multi_2_step` | 2 |  | as of december 31.2013 what was the ratio of the interest and penalty as a percent of the total unrecognized tax benefits |
| 135 | `finqa:test:CE/2016/page_19.pdf-2` | `single_subtract` | 1 | yes | what is the net change in the amount spent for research and development in 2015 compare to 2014? |
| 136 | `finqa:test:ABMD/2008/page_86.pdf-2` | `single_divide` | 1 |  | what is the maximum percentage of the june 2008 , contingent consideration for impella that must be satisfied in cash ? t |
| 137 | `finqa:test:MMM/2007/page_23.pdf-2` | `single_divide` | 1 |  | in 2007 what was the ratio of the interest expense to the interest income |
| 138 | `finqa:test:UNP/2016/page_52.pdf-3` | `multi_5_step` | 5 |  | what percentage of total operating revenues from 2014-2016 is the revenue from coal? |
| 139 | `finqa:test:PPG/2012/page_29.pdf-3` | `single_subtract` | 1 |  | what was the difference in millions of capital spending related to business acquisitions from 2010 to 2011? |
| 140 | `finqa:test:GS/2013/page_149.pdf-3` | `table_max` | 1 |  | in millions for 2013 and 2012 , what was maximum net derivative liabilities under bilateral agreements? |
| 141 | `finqa:test:MRO/2013/page_39.pdf-2` | `multi_2_step` | 2 |  | by what percentage did the average price of wti crude oil increase from 2011 to 2013? |
| 142 | `finqa:test:AMT/2003/page_102.pdf-2` | `multi_2_step` | 2 |  | what is the expected percentage change in aggregate principal payments of long-term debt from 2004 to 2005? |
| 143 | `finqa:test:JPM/2018/page_90.pdf-5` | `multi_2_step` | 2 |  | by how many basis points did net interest yield on average interest-earning assets 2013 managed basis improve form 2016 to 2017?\\n |
| 144 | `finqa:test:GS/2017/page_86.pdf-1` | `single_divide` | 1 |  | for the capital framework , what percent of the minimum supplementary leverage ratio consisted of a buffer? |
| 145 | `finqa:test:ETR/2013/page_21.pdf-1` | `multi_2_step` | 2 |  | what is the growth rate in net revenue for entergy wholesale commodities in 2012? |
| 146 | `finqa:test:GS/2018/page_69.pdf-1` | `multi_2_step` | 2 | yes | what are the total market making revenues in the consolidated statements of earnings of 2017 , in billions? |
| 147 | `finqa:test:GPN/2010/page_87.pdf-3` | `single_divide` | 1 |  | in 2010 what was the percent of the income tax benefit to the stock based compensation cost |
| 148 | `finqa:test:ETR/2004/page_212.pdf-2` | `single_divide` | 1 |  | what are the deferred fuel cost revisions as a percentage of 2004 net revenue? |
| 149 | `finqa:test:AES/2001/page_85.pdf-1` | `single_divide` | 1 |  | what percentage of scheduled maturities of total debt at december 31 , 2001 are due in 2002? |
| 150 | `finqa:test:MSI/2007/page_70.pdf-2` | `single_multiply` | 1 |  | in 2006 , what was the net sales to the segment 2019s top five customers in millions |
| 151 | `finqa:test:RSG/2018/page_135.pdf-2` | `multi_2_step` | 2 |  | what was the percentage decline in the equity from 2017 to 2018 actual |
| 152 | `finqa:test:RCL/2012/page_75.pdf-2` | `multi_2_step` | 2 |  | what was the percentage increase in the port call costs included from 2011 to 2012 |
| 153 | `finqa:test:CME/2017/page_40.pdf-5` | `comparison` | 1 |  | did the cme group inc . outperform the s&p 500 over 5 years? |
| 154 | `finqa:test:D/2002/page_87.pdf-4` | `multi_2_step` | 2 |  | what is the growth rate in rental expense included in other operations and maintenance expense in 2001 compare to 2000? |
| 155 | `finqa:test:AES/2001/page_33.pdf-2` | `single_subtract` | 1 |  | what was the difference in the companies high compared to its low sales price for the second quarter of 2001? |
| 156 | `finqa:test:BLL/2010/page_37.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in cash flows provided by ( used in ) operating activities including discontinued operations between 2008 and 2009? |
| 157 | `finqa:test:GS/2013/page_85.pdf-1` | `single_divide` | 1 |  | what percentage of total average securities and certain overnight cash deposits that are included in gce during 2013 were non-u.s . dollar-denominated? |
| 158 | `finqa:test:FBHS/2017/page_83.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in the weighted average fair value on the date of the award of the common stock |
| 159 | `finqa:test:UNP/2009/page_42.pdf-1` | `multi_2_step` | 2 | yes | what was the average cost per locomotive for the october 15 , 2009 purchase by the railroad? |
| 160 | `finqa:test:MAS/2017/page_27.pdf-1` | `multi_2_step` | 2 |  | what was the percentage cumulative total shareholder return on masco common stock for the five year period ended 2017? |
| 161 | `finqa:test:CME/2010/page_123.pdf-2` | `single_multiply` | 1 | yes | assuming all options in the compensation plans approved by security holders were exercised , what would be the deemed proceeds to the company? |
| 162 | `finqa:test:ABMD/2012/page_79.pdf-2` | `multi_2_step` | 2 | yes | how much of total future minimum lease payments are due currently? |
| 163 | `finqa:test:ADBE/2008/page_74.pdf-2` | `comparison` | 1 |  | is the weighted average useful life ( years ) for purchased technology greater than localization? |
| 164 | `finqa:test:IP/2006/page_38.pdf-2` | `single_divide` | 1 |  | what percentage of contractual obligations for future payments under existing debt and lease commitments and purchase obligations at december 31 , 2006 due in 2008 is attributable to total debt repayments? |
| 165 | `finqa:test:AES/2010/page_227.pdf-4` | `multi_2_step` | 2 |  | what is the annual interest cost savings by the company redeeming the 8.75% ( 8.75 % ) second priority senior secured notes? |
| 166 | `finqa:test:JPM/2009/page_175.pdf-2` | `single_subtract` | 1 |  | excluding derivatives , what are net 2008 trading assets , in millions? |
| 167 | `finqa:test:DG/2009/page_77.pdf-1` | `single_divide` | 1 |  | what is the yearly depreciation rate for land improvements? |
| 168 | `finqa:test:SLG/2001/page_48.pdf-1` | `comparison` | 1 |  | was the fair value of the interest rate collar greater than the fair value of the interest rate swap? |
| 169 | `finqa:test:EMR/2017/page_78.pdf-2` | `single_multiply` | 1 |  | at the average grant date fair value per share what is the value in thousands of the shares outstanding but not yet earned under incentive shares at the end of the year ? \\n |
| 170 | `finqa:test:SNA/2013/page_84.pdf-3` | `single_divide` | 1 |  | what percentage of trade and other accounts receivable are considered as doubtful receivables in 2013 |
| 171 | `finqa:test:UNP/2006/page_15.pdf-3` | `single_divide` | 1 |  | what percent of total route miles are main line in 2006? |
| 172 | `finqa:test:DRE/2008/page_46.pdf-3` | `multi_4_step` | 4 |  | what was the average basic net income available for common shareholders from 2006 to 2008 in millions |
| 173 | `finqa:test:MSI/2007/page_70.pdf-1` | `multi_3_step` | 3 | yes | what was the average segment net sales from 2005 to 2007 in millions |
| 174 | `finqa:test:JKHY/2017/page_26.pdf-2` | `single_divide` | 1 |  | jkhy's total 5 year return was what percent of the peer group? |
| 175 | `finqa:test:GIS/2017/page_31.pdf-1` | `single_divide` | 1 |  | in 2017 what was the percent of the total future estimated cash payments under existing contractual obligations associated with long-term debt that was due in 2018 |
| 176 | `finqa:test:GPN/2010/page_89.pdf-4` | `multi_4_step` | 4 |  | what is the percentage change in the total fair value of non-vested shares from 2009 to 2010? |
| 177 | `finqa:test:GS/2017/page_132.pdf-1` | `table_max` | 1 |  | in millions for 2017 and 2016 , what was the greatest amount of derivatives? |
| 178 | `finqa:test:JPM/2009/page_175.pdf-4` | `multi_3_step` | 3 |  | what is the total equity in 2009 , in millions of dollars? |
| 179 | `finqa:test:IP/2006/page_38.pdf-4` | `single_divide` | 1 | yes | in 2007 what was the percent of the total debt compared to lease obligations and purchase obligations as part of the contractual obligations for future payments |
| 180 | `finqa:test:GS/2013/page_149.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in collateral posted from 2012 to 2013? |
| 181 | `finqa:test:PNC/2012/page_65.pdf-3` | `single_divide` | 1 |  | in 2012 what was the percent of the total amortized assets that was made of total securities available for sale |
| 182 | `finqa:test:FBHS/2017/page_22.pdf-2` | `single_multiply` | 1 |  | what was the amount of sales in that went to international markets in millions |
| 183 | `finqa:test:PPG/2012/page_29.pdf-4` | `single_subtract` | 1 | yes | what was the difference in millions of capital spending related to business acquisitions from 2011 to 2012? |
| 184 | `finqa:test:NWS/2017/page_119.pdf-1` | `single_divide` | 1 |  | how much in millions will be amortized each year for the acquired technology related to the realtor.com ae website? |
| 185 | `finqa:test:AMT/2006/page_113.pdf-2` | `single_subtract` | 1 |  | what is the net change in the balance of employee separations liability during 2004? |
| 186 | `finqa:test:IPG/2008/page_72.pdf-4` | `single_divide` | 1 | yes | what percentage of balance of unrecognized tax benefits at the end of 2008 would impact the effective tax rate if recognized? |
| 187 | `finqa:test:UNP/2007/page_25.pdf-4` | `single_subtract` | 1 |  | what was change in millions of free cash flow from 2005 to 2006? |
| 188 | `finqa:test:AES/2002/page_128.pdf-2` | `single_subtract` | 1 |  | what was the decrease in rental expense ( millions ) for operating leases in continuing operations from 2003 to 2003? |
| 189 | `finqa:test:AWK/2018/page_146.pdf-1` | `multi_2_step` | 2 |  | what is total intangible asset amortization expense ( millions ) for the years ended december 31 , 2018 , 2017 and 2016? |
| 190 | `finqa:test:RSG/2016/page_139.pdf-2` | `single_divide` | 1 |  | as of december 31 , 2016 what was the percent of the outstanding authorized purchase capacity of the the october 2015 plan |
| 191 | `finqa:test:MKTX/2012/page_42.pdf-3` | `multi_2_step` | 2 |  | by how much did the low of mktx stock increase from 2011 to march 2012? |
| 192 | `finqa:test:GS/2012/page_142.pdf-4` | `table_max` | 1 | yes | in millions for 2012 2011 what was the maximum net derivative liabilities under bilateral agreements? |
| 193 | `finqa:test:UNP/2018/page_74.pdf-1` | `multi_2_step` | 2 |  | what is the 2019 to 2020 projected growth rate for operating lease payments? |
| 194 | `finqa:test:LMT/2015/page_89.pdf-4` | `single_divide` | 1 |  | in november 2015 what was the percent of the costs associated with issuing of the notes under the 364-day facility used to finance the acquisition |
| 195 | `finqa:test:FIS/2017/page_64.pdf-1` | `multi_2_step` | 2 |  | what is the percentage change in revenue generated from non-us currencies from 2016 to 2017? |
| 196 | `finqa:test:APD/2018/page_30.pdf-2` | `multi_2_step` | 2 | yes | what is the increase observed in the payment of dividends during 2017 and 2018? |
| 197 | `finqa:test:BLL/2010/page_35.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in net sales for the discontinued operations between 2008 and 2009? |
| 198 | `finqa:test:C/2018/page_175.pdf-4` | `single_divide` | 1 |  | what was the percent of the principal transactions revenue associated with foreign exchange risks in 2017 |
| 199 | `finqa:test:UPS/2010/page_52.pdf-4` | `multi_2_step` | 2 |  | what percentage of contractual obligations and commitments in total are debt principal and debt interest? |
| 200 | `finqa:test:ETR/2016/page_374.pdf-4` | `single_divide` | 1 |  | for 2016 , what percentage of net revenue was due to the retail electric price adjustment? |
| 201 | `finqa:test:GPN/2010/page_89.pdf-1` | `multi_2_step` | 2 |  | in 2009 what was the percentage change in the non-vested at may 31 2009 |
| 202 | `finqa:test:MRO/2004/page_125.pdf-1` | `table_average` | 1 |  | what was the average ending balance in the discounted ending cash flow balance? |
| 203 | `finqa:test:ZBH/2008/page_57.pdf-2` | `single_divide` | 1 |  | what percent of total contractual obligations is categorized as long term debt? |
| 204 | `finqa:test:CMCSA/2008/page_36.pdf-2` | `single_divide` | 1 |  | scalable infrastructure represents what percent of capital expenditures incurred the cable segment during 2008? |
| 205 | `finqa:test:ETR/2011/page_301.pdf-3` | `multi_5_step` | 5 |  | what was entergy gulf states louisiana 2019s receivables from the money pool from 2008 to 2011 in millions |
| 206 | `finqa:test:BLL/2010/page_35.pdf-1` | `single_divide` | 1 |  | productivity in the plastics business measured by million $ sales per employee was what in 2009? |
| 207 | `finqa:test:ETR/2008/page_442.pdf-2` | `multi_3_step` | 3 | yes | what portion of the total restricted units will vest in 2011? |
| 208 | `finqa:test:AAPL/2006/page_100.pdf-3` | `table_max` | 1 | yes | what was the greatest provision for income taxes , in millions? |
| 209 | `finqa:test:ETR/2004/page_212.pdf-3` | `single_subtract` | 1 |  | what is the net change in net revenue during 2004 for entergy louisiana? |
| 210 | `finqa:test:INTC/2015/page_41.pdf-1` | `single_divide` | 1 |  | what percentage of total facilities as measured in square feet are owned? |
| 211 | `finqa:test:HOLX/2007/page_93.pdf-2` | `single_divide` | 1 |  | what portion of the issued securities is approved by security holders? |
| 212 | `finqa:test:RSG/2013/page_123.pdf-2` | `multi_2_step` | 2 |  | what was the growth of the weighted-average estimated fair values of stock options granted from 2012 to 2013 |
| 213 | `finqa:test:AWK/2014/page_121.pdf-1` | `multi_2_step` | 2 | yes | what was the net change in tax positions in 2014 |
| 214 | `finqa:test:K/2006/page_52.pdf-1` | `single_divide` | 1 |  | what percent of net cash provided by operations is retained as cashflow in 2006? |
| 215 | `finqa:test:ETR/2016/page_374.pdf-2` | `multi_2_step` | 2 |  | what is the growth rate in net revenue in 20016 for entergy mississippi , inc.? |
| 216 | `finqa:test:TFX/2015/page_89.pdf-2` | `single_divide` | 1 |  | what portion of the total 2015 restructuring programs is related to facility closer costs? |
| 217 | `finqa:test:HIG/2011/page_53.pdf-2` | `multi_2_step` | 2 |  | in 2011 what was the summary of environmental reserves as of december 31 , 2011 |
| 218 | `finqa:test:STT/2007/page_111.pdf-3` | `multi_2_step` | 2 | yes | what is the growth rate in the balance of standby letters of credit from 2006 to 2007? |
| 219 | `finqa:test:STT/2011/page_69.pdf-2` | `single_divide` | 1 |  | what is the approximate total number of workforce before the restructuring program? |
| 220 | `finqa:test:DISH/2010/page_117.pdf-2` | `single_divide` | 1 |  | what percentage of total minimum lease payments are due in 2015? |
| 221 | `finqa:test:CB/2008/page_229.pdf-4` | `single_divide` | 1 |  | in 2009 what was the ratio of the statutory capital and surplus to the statutory net income of the bermuda subsidiaries |
| 222 | `finqa:test:MSI/2014/page_76.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in the weighted-average estimated fair value of employee stock options granted during from 2013 to 2014 |
| 223 | `finqa:test:GPN/2008/page_78.pdf-2` | `single_divide` | 1 |  | what percentage of net assets acquired was considered goodwill? |
| 224 | `finqa:test:AMT/2008/page_107.pdf-2` | `single_subtract` | 1 |  | in 2006 what was percentage change in the employee separations liabilities |
| 225 | `finqa:test:JPM/2009/page_175.pdf-3` | `single_divide` | 1 |  | in 2008 what was the ratio of the trading assets derivatives - receivables to the payables |
| 226 | `finqa:test:PNC/2008/page_122.pdf-1` | `single_divide` | 1 |  | for national city-sponsored securitization qspes at december 31 , 2008 , automobile was what percent of credit card assets? |
| 227 | `finqa:test:UA/2011/page_69.pdf-1` | `multi_2_step` | 2 |  | what was the percentage decrease in the weighted average interest rates on outstanding borrowings from 2010 to 2011 |
| 228 | `finqa:test:C/2008/page_22.pdf-4` | `single_add` | 1 |  | what was the total pretax gains in millions for the sale so mastercard shares from 2006 to 2007? |
| 229 | `finqa:test:DRE/2002/page_15.pdf-2` | `multi_3_step` | 3 |  | what is the percent change in general and administrative expense from 2000 to 2001? |
| 230 | `finqa:test:AMT/2003/page_27.pdf-1` | `multi_2_step` | 2 |  | what portion of the boston property will be offered for sub-lease? |
| 231 | `finqa:test:INTC/2015/page_41.pdf-3` | `single_divide` | 1 |  | what is the percent of the square foot in millions of owned facilities in the other countries to the of the total owned facilities |
| 232 | `finqa:test:MAS/2017/page_27.pdf-4` | `single_divide` | 1 |  | what was the ratio of the value of the common stock masco to s&p 500 index in 2015 |
| 233 | `finqa:test:MAS/2012/page_26.pdf-2` | `multi_2_step` | 2 |  | what was the percent of the increase in the performance of the s&p 500 index from 2008 to 2009 |
| 234 | `finqa:test:PNC/2012/page_65.pdf-1` | `multi_2_step` | 2 |  | what percentage of the total carrying amount of investment securities is the securities held to maturity? |
| 235 | `finqa:test:UNP/2006/page_15.pdf-4` | `single_divide` | 1 |  | what percent of total route miles are main line in 2005? |
| 236 | `finqa:test:GRMN/2008/page_85.pdf-2` | `multi_5_step` | 5 |  | what is the difference between the growth of the balance throughout the fiscal year , during 2007 and 2008? |
| 237 | `finqa:test:ZBH/2008/page_57.pdf-3` | `multi_2_step` | 2 |  | what percent of total contractual obligations is due 2012 or after? |
| 238 | `finqa:test:CDNS/2018/page_66.pdf-3` | `single_subtract` | 1 |  | what is the net effect of the adoption of new accounting standards? |
| 239 | `finqa:test:GS/2013/page_63.pdf-1` | `table_average` | 1 |  | in millions for 2013 and 2012 , what was average total assets? |
| 240 | `finqa:test:JPM/2010/page_281.pdf-2` | `single_divide` | 1 |  | as of december 31 , 2009 , what percentage of the collateral that it was able to sell , repledge , deliver , or otherwise use was actually used for these purposes? |
| 241 | `finqa:test:LMT/2014/page_91.pdf-2` | `multi_3_step` | 3 | yes | what was the average employee contributions from 2012 to 2014 |
| 242 | `finqa:test:MAS/2017/page_27.pdf-3` | `multi_2_step` | 2 |  | what was the percentage of the growth of the s&p 500 index from 2016 to 2017 |
| 243 | `finqa:test:LMT/2015/page_89.pdf-1` | `single_divide` | 1 | yes | in 2015 what was the net profit margin |
| 244 | `finqa:test:HWM/2018/page_96.pdf-2` | `multi_3_step` | 3 |  | considering the average exercise price of options , what is the increase in the total value of stock options observed during 2016 and 2017 , in millions of dollars? |
| 245 | `finqa:test:RSG/2012/page_93.pdf-1` | `single_subtract` | 1 |  | what was the change in the allowance for doubtful accounts in 2012 |
| 246 | `finqa:test:AMT/2016/page_49.pdf-4` | `single_divide` | 1 |  | what is the average number of shares per registered holder as of february 17 , 2017? |
| 247 | `finqa:test:UPS/2007/page_98.pdf-2` | `single_multiply` | 1 |  | what is the average expected dividend per share in 2007? |
| 248 | `finqa:test:CME/2017/page_40.pdf-3` | `single_divide` | 1 |  | in 2017 what was the ratio of the the cme group inc . stock perfomamce to the s&p |
| 249 | `finqa:test:GS/2014/page_40.pdf-2` | `multi_2_step` | 2 | yes | what is the growth rate in operating expenses in 2013? |
| 250 | `finqa:test:AAPL/2006/page_100.pdf-2` | `single_multiply` | 1 |  | what was the 2005 tax expense? |
| 251 | `finqa:test:AMT/2005/page_102.pdf-3` | `multi_2_step` | 2 | yes | what is the percentage change in impairment charges and net losses from 2003 to 2004? |
| 252 | `finqa:test:GS/2012/page_142.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in net derivative liabilities under bilateral agreements between 2011 and 2012? |
| 253 | `finqa:test:AAL/2013/page_172.pdf-1` | `single_divide` | 1 |  | what portion of the total bankruptcy settlement obligations are related to labor deemed claims? |
| 254 | `finqa:test:JPM/2012/page_140.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in lending-related commitments from 2011 to 2012? |
| 255 | `finqa:test:IP/2006/page_31.pdf-1` | `single_divide` | 1 |  | what percentage of 2006 industrial packaging sales are containerboard sales? |
| 256 | `finqa:test:C/2008/page_65.pdf-2` | `multi_2_step` | 2 |  | what was the percentage increase in citigroup 2019s allowance for loan losses attributable to the consumer portfolio from 2007 to 2008 |
| 257 | `finqa:test:C/2009/page_243.pdf-2` | `single_divide` | 1 |  | at december 31 2009 what was the ratio of the aggregate cost to the fair value of the loans held-for-sale that are carried at locom |
| 258 | `finqa:test:PNC/2012/page_68.pdf-1` | `multi_2_step` | 2 |  | by what percentage did total residential mortgages increase from 2011 to 2012? |
| 259 | `finqa:test:HOLX/2008/page_143.pdf-2` | `single_divide` | 1 |  | what potion of the r2 acquisition is paid in cash? |
| 260 | `finqa:test:NWS/2019/page_116.pdf-2` | `single_subtract` | 1 |  | what was the difference in millions of deferral of revenue and recognition of deferred revenue for the fiscal year ended june 30 , 2019? |
| 261 | `finqa:test:MO/2016/page_19.pdf-4` | `multi_2_step` | 2 |  | what is the roi of an investment in s&p500 from december 2011 to december 2013? |
| 262 | `finqa:test:LKQ/2016/page_87.pdf-1` | `multi_2_step` | 2 | yes | what was the percentage change in rental expense for operating leases from 2014 to 2015? |
| 263 | `finqa:test:MRK/2013/page_125.pdf-3` | `single_divide` | 1 |  | what was the ratio of interest and penalties associated with uncertain tax positions in 2013 to 2012 |
| 264 | `finqa:test:FIS/2016/page_9.pdf-2` | `multi_2_step` | 2 |  | what is the growth rate for the ifs segment in 2016? |
| 265 | `finqa:test:PPG/2006/page_42.pdf-4` | `single_subtract` | 1 | yes | what was the change in millions in the reserve for product warranties from 2005 to 2006? |
| 266 | `finqa:test:UAA/2016/page_42.pdf-4` | `multi_2_step` | 2 |  | what was the percentage change in working capital from 2015 to 2016? |
| 267 | `finqa:test:BLL/2011/page_32.pdf-1` | `multi_2_step` | 2 | yes | what is the growth rate in net sales from 2010 to 2011? |
| 268 | `finqa:test:STT/2009/page_25.pdf-2` | `multi_2_step` | 2 |  | what was the percent change in the aggregate net asset values of the collateral pools underlying ssga lending funds between 2008 and 2009? |
| 269 | `finqa:test:AMT/2003/page_27.pdf-3` | `single_divide` | 1 |  | in 2004 following the consolidation of the business operation what was the percentage of rental square feet in boston up for re-lease |
| 270 | `finqa:test:AMT/2008/page_94.pdf-1` | `single_divide` | 1 |  | as of december 31 , 2008 , what was the percent of the maturities in 2012 of the aggregate carrying value of long-term debt , including capital leases |
| 271 | `finqa:test:IP/2006/page_35.pdf-4` | `single_subtract` | 1 |  | what was the difference in the increase in the cash in working capital in 2006 compared with the increase in 2005 in millions |
| 272 | `finqa:test:GIS/2017/page_31.pdf-3` | `single_add` | 1 |  | what are the total off-balance sheet obligations , ( in millions ) ? |
| 273 | `finqa:test:ETR/2008/page_298.pdf-3` | `single_subtract` | 1 |  | how is the cash flow of entergy gulf states louisiana affected by the balance from money pool from 2007 to 2008 , in thousands? |
| 274 | `finqa:test:GS/2013/page_220.pdf-2` | `multi_5_step` | 5 |  | what was the difference in percentage cumulative total return for goldman sachs group inc . and the s&p 500 index for the five year period ending 12/31/13? |
| 275 | `finqa:test:TMUS/2017/page_29.pdf-4` | `single_divide` | 1 |  | what is the ratio of the office space throughout the us to the office space for the corporate headquarters in bellevue |
| 276 | `finqa:test:ETR/2017/page_372.pdf-3` | `multi_2_step` | 2 |  | what percent did net revenue decrease between 2016 and 2017? |
| 277 | `finqa:test:GIS/2018/page_110.pdf-3` | `single_divide` | 1 |  | what was the percent of the total noncancelable future lease commitments for operating leases that was due in 2020 |
| 278 | `finqa:test:ETR/2004/page_212.pdf-1` | `multi_2_step` | 2 | yes | what is the growth rate in net revenue in 2004 for entergy louisiana? |
| 279 | `finqa:test:MAS/2012/page_26.pdf-1` | `single_divide` | 1 | yes | as of december 2012 what was the ratio of the percent of the outstanding shares of the authorized repurchase of the company common stock |
| 280 | `finqa:test:BLK/2012/page_33.pdf-1` | `multi_2_step` | 2 |  | what is the percent change in long-term component changes from 12/31/2011 to 12/31/2012? |
| 281 | `finqa:test:STT/2009/page_127.pdf-3` | `multi_2_step` | 2 |  | what was the percent change in net unrealized loss on available-for-sale securities between 2008 and 2009? |
| 282 | `finqa:test:AWK/2014/page_121.pdf-3` | `multi_2_step` | 2 |  | by how much did company 2019s gross liability , excluding interest and penalties , for unrecognized tax benefits increase from 2014 to 2014? |
| 283 | `finqa:test:PNC/2012/page_68.pdf-3` | `multi_2_step` | 2 |  | what was the average for "other" loans held in 2012 and 2011? |
| 284 | `finqa:test:GS/2018/page_78.pdf-1` | `table_min` | 1 |  | in billions for 2018 , 2017 , and 2016 , what was the lowest amount of alternative investments? |
| 285 | `finqa:test:DVN/2018/page_35.pdf-1` | `single_divide` | 1 |  | what was the ratio in the total tax expense from 2018 to 2017 |
| 286 | `finqa:test:GS/2017/page_179.pdf-3` | `comparison` | 1 |  | did the firm cancel more stock options during 2017 than it repurchased in common shares? |
| 287 | `finqa:test:PPG/2006/page_42.pdf-1` | `multi_2_step` | 2 | yes | what would the cash expense for product warranties be in 2007 if the amounts increased the same percentage as in 2006 ( in millions ) ? |
| 288 | `finqa:test:ABMD/2007/page_78.pdf-4` | `multi_2_step` | 2 |  | what is the growth rate in the weighted average fair value for options granted between 2005 to 2006? |
| 289 | `finqa:test:GIS/2015/page_62.pdf-1` | `single_divide` | 1 |  | in may 2015 what was the ratio of the unrealized losses from interest rate cash flow hedges to the unrealized gains from foreign currency cash flow hedges |
| 290 | `finqa:test:UPS/2012/page_32.pdf-2` | `multi_5_step` | 5 |  | what was the difference in percentage total cumulative return on investment for united parcel service inc . versus the dow jones transportation average for the five years ended 12/31/2012? |
| 291 | `finqa:test:GPN/2013/page_92.pdf-2` | `single_subtract` | 1 |  | what is the percentage change in the expected minimum payments from 2014 to 2015? |
| 292 | `finqa:test:PKG/2013/page_88.pdf-1` | `single_divide` | 1 |  | as of december 312013 what was the ratio of the equity compensation plans approved by security holders remaining to be issued to the amount to be issued upon exercise of outstanding |
| 293 | `finqa:test:HOLX/2007/page_126.pdf-1` | `multi_3_step` | 3 |  | what is the total value of intangible asset taken into account when setting up the estimated purchase price? |
| 294 | `finqa:test:KHC/2018/page_132.pdf-3` | `single_subtract` | 1 |  | what is the net increase in outstanding shares during the period of 2016 to 2018 , in millions? |
| 295 | `finqa:test:AWK/2012/page_117.pdf-1` | `single_add` | 1 |  | what was total liability reflected as other long-term liabilities in the accompanying consolidated balance sheets for december 31 , 2012 and 2011 in millions? |
| 296 | `finqa:test:SLB/2012/page_56.pdf-2` | `single_add` | 1 |  | the stock repurchase program reduced shares outstanding by how many million shares in the period? |
| 297 | `finqa:test:AOS/2010/page_18.pdf-1` | `multi_5_step` | 5 |  | what was the difference in the cumulative total return for a o smith corp and the s&p small cap 600 index for the five year period ended 12/31/10? |
| 298 | `finqa:test:AWK/2017/page_148.pdf-1` | `multi_2_step` | 2 |  | by what percentage did average borrowings decrease from 2016 to 2017? |
| 299 | `finqa:test:PPG/2018/page_85.pdf-4` | `single_divide` | 1 | yes | what percent of total reserves for environmental contingencies are related to new jersey chrome in 2018? |
| 300 | `finqa:test:PNC/2012/page_174.pdf-2` | `single_add` | 1 |  | what was the two-year total for specific reserves in the alll , in millions? |
| 301 | `finqa:test:AMT/2007/page_29.pdf-4` | `single_divide` | 1 |  | what portion of the woburn property is used by the american tower corporation? |
| 302 | `finqa:test:GS/2013/page_149.pdf-4` | `table_min` | 1 |  | in millions for 2013 and 2012 , what was the minimum collateral posted? |
| 303 | `finqa:test:DISCA/2011/page_49.pdf-2` | `multi_2_step` | 2 |  | what was the percentage cumulative total shareholder return on discb from september 18 , 2008 to december 31 , 2011? |
| 304 | `finqa:test:ABMD/2007/page_78.pdf-3` | `multi_2_step` | 2 | yes | what is the growth rate in the weighted average fair value for options granted between 2006 to 2007? |
| 305 | `finqa:test:ETR/2008/page_442.pdf-1` | `multi_2_step` | 2 |  | what is the total number of restricted units expected to vest in the upcoming years? |
| 306 | `finqa:test:NCLH/2018/page_64.pdf-4` | `multi_2_step` | 2 |  | how much did interest with libor change from year 1 to years 3-5? |
| 307 | `finqa:test:IPG/2017/page_92.pdf-4` | `single_divide` | 1 |  | what portion of the total contingent acquisition payments is related to deferred acquisition payments? |
| 308 | `finqa:test:FBHS/2017/page_22.pdf-1` | `single_divide` | 1 |  | in 2017 what was the ratio of the cabinets sales to the doors |
| 309 | `finqa:test:GRMN/2008/page_73.pdf-1` | `single_divide` | 1 |  | considering the contractual obligations in which payments due by 1-3 years , what is the percentage of the operating leases in relation to the total obligations? |
| 310 | `finqa:test:ADBE/2008/page_89.pdf-3` | `multi_2_step` | 2 |  | the combined amount of accrued interest and penalties related to tax positions taken on our tax returns and included in non-current income taxes payable was what percent of the total ending balance as of november 28 2008? |
| 311 | `finqa:test:UNP/2011/page_24.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in free cash flow from 2009 to 2010? |
| 312 | `finqa:test:MRO/2017/page_96.pdf-1` | `table_max` | 1 |  | what was the greatest ultimate trend rate for health care costs ? 4.70% ( 4.70 % ) 4.50% ( 4.50 % ) 4.50% ( 4.50 % ) |
| 313 | `finqa:test:PNC/2012/page_100.pdf-2` | `multi_2_step` | 2 |  | for home equity unresolved asserted indemnification and repurchase claims in millions , what was average balance for december 31 2012 and december 31 2011? |
| 314 | `finqa:test:BKR/2017/page_56.pdf-3` | `multi_2_step` | 2 | yes | what is the net change in cash during 2015? |
| 315 | `finqa:test:IP/2009/page_84.pdf-4` | `multi_2_step` | 2 |  | what was the sum of the temporary differences between 2007 and 2009 in billions |
| 316 | `finqa:test:HIG/2004/page_140.pdf-2` | `single_add` | 1 |  | what is the total effect of reclassifying certain separate accounts to general account on the net income and other comprehensive income? |
| 317 | `finqa:test:GIS/2019/page_68.pdf-1` | `single_subtract` | 1 |  | what is the sales growth rate from 2017 to 2018? |
| 318 | `finqa:test:AES/2002/page_128.pdf-4` | `multi_3_step` | 3 | yes | what was the average rental expense in millions for 2000 through 2002? |
| 319 | `finqa:test:UA/2011/page_69.pdf-2` | `single_divide` | 1 |  | as of december 312012 what was the percent of the scheduled maturities of long term debt as part of the long term debt |
| 320 | `finqa:test:JPM/2008/page_117.pdf-2` | `multi_2_step` | 2 |  | what was the total impact on dva of a 1 basis point increase in jpmorgan chase credit spread for 2008 and 2007? |
| 321 | `finqa:test:AMAT/2018/page_33.pdf-1` | `multi_2_step` | 2 |  | what is the roi for applied materials if the investment made on october 2013 was sold 2 years later? |
| 322 | `finqa:test:SNA/2013/page_34.pdf-2` | `multi_2_step` | 2 |  | what is the return on investment if $ 100 are invested in s&p500 at the end of 2008 and sold at the end of 2010? |
| 323 | `finqa:test:PPG/2008/page_52.pdf-3` | `single_subtract` | 1 | yes | what was the net change in the accrued liability for unrecognized tax benefits from 2007 to 2008? |
| 324 | `finqa:test:SNA/2007/page_69.pdf-3` | `multi_3_step` | 3 |  | what was the percentage change in the minority interest from 2005 to 2006 |
| 325 | `finqa:test:JKHY/2017/page_26.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in the s&p 500 stock performance from 2014 to 2015 |
| 326 | `finqa:test:LMT/2015/page_89.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in net earnings from continuing operations from 2014 to 2015? |
| 327 | `finqa:test:RL/2008/page_23.pdf-1` | `single_divide` | 1 |  | what percentage of factory retail stores as of march 29 , 2008 where located in europe? |
| 328 | `finqa:test:STT/2009/page_127.pdf-4` | `single_multiply` | 1 |  | what is the total value , in dollars , of the shares purchasable under the warrant? |
| 329 | `finqa:test:ABMD/2008/page_86.pdf-1` | `single_subtract` | 1 |  | assuming the same level of settlements as in fiscal 2007 , what would be the ending balance at march 31 2008 in millions for unrecognized tax benefits?\\n |
| 330 | `finqa:test:DRE/2005/page_30.pdf-1` | `single_divide` | 1 |  | what was the ratio of the after tax gains of in 2004 compared to 2003 in dollars |
| 331 | `finqa:test:ABMD/2005/page_29.pdf-3` | `multi_2_step` | 2 |  | what is the percentage change in the risk-free rate from 2003 to 2004? |
| 332 | `finqa:test:ILMN/2003/page_58.pdf-3` | `multi_5_step` | 5 |  | what was the difference in cumulative total stockholder return percentage for illumina inc . common stock versus the nasdaq pharmaceutical index for the four years end 2003? |
| 333 | `finqa:test:GS/2012/page_142.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in collateral posted between 2011 and 2012? |
| 334 | `finqa:test:JKHY/2019/page_18.pdf-3` | `comparison` | 1 |  | was the five year total return of the 2019 peer group greater than the 2018 peer group? |
| 335 | `finqa:test:ETR/2004/page_239.pdf-3` | `multi_2_step` | 2 |  | what is the growth rate in net revenue for entergy mississippi , inc . in 2003? |
| 336 | `finqa:test:MS/2013/page_139.pdf-1` | `comparison` | 1 |  | did the company have more exposure to the insurance industry than the real estate industry in its derivative portfolio? |
| 337 | `finqa:test:MO/2014/page_62.pdf-1` | `multi_2_step` | 2 | yes | what is the percent change in earnings for basic and diluted eps from 2013 to 2014? |
| 338 | `finqa:test:FIS/2016/page_45.pdf-1` | `multi_2_step` | 2 |  | what is the percentage increase in cash flows from operations from 2015 to 2016? |
| 339 | `finqa:test:SNA/2007/page_49.pdf-4` | `multi_2_step` | 2 |  | what was the percentage change in the cash dividends paid per common share from 2006 to 2007 |
| 340 | `finqa:test:ETR/2004/page_239.pdf-2` | `single_subtract` | 1 | yes | what is the net change in net revenue entergy mississippi , inc . during 2003? |
| 341 | `finqa:test:ETFC/2018/page_153.pdf-2` | `single_divide` | 1 |  | what was the ratio of the pre-tax gain on the securities transferred from held-to-maturity securities to available-for-sale securities \\n |
| 342 | `finqa:test:UPS/2016/page_114.pdf-1` | `single_subtract` | 1 |  | what was the change in millions of vehicles from 2015 to 2016? |
| 343 | `finqa:test:DVN/2015/page_79.pdf-2` | `multi_3_step` | 3 |  | in years , what is the average contractual term for 2013 , 2014 , 2015? |
| 344 | `finqa:test:AWK/2013/page_122.pdf-3` | `single_divide` | 1 |  | what is awk's 2012 unrecognized tax benefit as a percentage of gross liabilities? |
| 345 | `finqa:test:AES/2002/page_128.pdf-1` | `single_divide` | 1 |  | total discontinued operations represent what percentage of total future minimum lease commitments? |
| 346 | `finqa:test:AMT/2007/page_127.pdf-2` | `multi_2_step` | 2 | yes | based on the the pricing model what was the percentage change in the weighted average risk-free interest rate from 2005 to 2007 |
| 347 | `finqa:test:RSG/2010/page_98.pdf-2` | `single_divide` | 1 |  | as of december 31 , 2010 what was the ratio of the restricted cash and restricted marketable securities to the allowance for doubtful accounts |
| 348 | `finqa:test:GIS/2017/page_31.pdf-4` | `single_divide` | 1 |  | in 2018 what was the ratio of anticipated benefits payments from our unfunded postemployment benefit plans to the deferred compensation |
| 349 | `finqa:test:LKQ/2016/page_87.pdf-3` | `multi_2_step` | 2 |  | what was the cumulative rental expense from 2014 to 2016 in millions |
| 350 | `finqa:test:CMCSA/2015/page_112.pdf-1` | `single_subtract` | 1 |  | what was the change in unrecognized tax benefits from the end of 2013 to the end of 2014? |
| 351 | `finqa:test:DRE/2012/page_40.pdf-1` | `multi_2_step` | 2 |  | what was the percentage reduction second generation tenant improvements |
| 352 | `finqa:test:SNA/2018/page_31.pdf-3` | `single_multiply` | 1 |  | what is the total cash outflow for the share purchased during november 2018? |
| 353 | `finqa:test:GS/2015/page_188.pdf-2` | `single_divide` | 1 |  | what percentage of future minimum rental payments are due in 2018? |
| 354 | `finqa:test:CMCSA/2015/page_112.pdf-2` | `single_subtract` | 1 |  | what was the change in unrecognized tax benefits from the end of 2014 to the end of 2015? |
| 355 | `finqa:test:PNC/2012/page_100.pdf-1` | `single_subtract` | 1 |  | for home equity unresolved asserted indemnification and repurchase claims in millions , what was the change between december 31 2012 and december 31 2011?\\n\\n\\n\\n |
| 356 | `finqa:test:PKG/2002/page_52.pdf-2` | `multi_2_step` | 2 |  | what is the total value of the balance of options as of december 31 , 2002 , in millions? |
| 357 | `finqa:test:UPS/2007/page_49.pdf-4` | `table_sum` | 2 |  | what percentage of the total expected cash outflow to satisfy contractual obligations and commitments as of december 31 , 2007 , is pension fundings? |
| 358 | `finqa:test:AMT/2007/page_127.pdf-3` | `multi_2_step` | 2 |  | what is the growth rate in the price of shares purchased by employees from 2005 to 2006? |
| 359 | `finqa:test:AAL/2014/page_15.pdf-1` | `single_divide` | 1 | yes | what percentage of approximate number of active full-time equivalent employees consist of u.s airways employees? |
| 360 | `finqa:test:ZBH/2009/page_58.pdf-3` | `multi_2_step` | 2 |  | what was the percent change in operating leases between 2011/12 and 2013/4? |
| 361 | `finqa:test:IP/2006/page_31.pdf-3` | `single_divide` | 1 |  | what was the industrial packaging profit margin in 2004 |
| 362 | `finqa:test:ANSS/2012/page_93.pdf-2` | `multi_2_step` | 2 | yes | what was the percentage change in the royalty fees are reported in cost of goods sold from 2011 to 2012 |
| 363 | `finqa:test:ETR/2016/page_23.pdf-3` | `multi_2_step` | 2 | yes | what would 2015 net revenue have been in millions assuming there was no impact from both the retail electric price change and the impact of volume/weather in the year? |
| 364 | `finqa:test:MMM/2013/page_75.pdf-1` | `single_divide` | 1 | yes | what was the ratio of the company contribution in 2011 to the amount in 2013 to the us pension contributions |
| 365 | `finqa:test:VNO/2014/page_57.pdf-1` | `single_subtract` | 1 |  | what was the five year change in the vornado realty trust index? |
| 366 | `finqa:test:ETR/2016/page_150.pdf-1` | `multi_4_step` | 4 |  | what is the total expected payments on the bonds for the next 5 years for entergy louisiana investment recovery funding? |
| 367 | `finqa:test:JPM/2009/page_175.pdf-1` | `single_subtract` | 1 | yes | excluding derivatives , what are net 2009 trading assets , in millions? |
| 368 | `finqa:test:HUM/2017/page_118.pdf-4` | `multi_3_step` | 3 |  | what was the average amortization expense between 2015 and 2017 |
| 369 | `finqa:test:MKTX/2004/page_99.pdf-3` | `single_add` | 1 | yes | in 2004 and 2003 , what were the total shares of common stock that were issued to employees? |
| 370 | `finqa:test:BLL/2006/page_67.pdf-3` | `single_divide` | 1 |  | what percentage of total net assets acquired were goodwill? |
| 371 | `finqa:test:HOLX/2006/page_100.pdf-2` | `single_divide` | 1 |  | what percentage of the estimated purchase price is developed technology and know how? |
| 372 | `finqa:test:UNP/2018/page_74.pdf-4` | `single_divide` | 1 |  | what percent of total minimum capital leases payments are due in 2020? |
| 373 | `finqa:test:MRO/2008/page_45.pdf-4` | `table_sum` | 1 |  | what was total pipeline barrels handled ( thousands of barrels per day ) for the three year period? |
| 374 | `finqa:test:AMT/2005/page_102.pdf-2` | `multi_2_step` | 2 | yes | what is the percentage change in impairment charges and net losses from 2004 to 2005? |
| 375 | `finqa:test:UPS/2007/page_49.pdf-1` | `table_sum` | 1 |  | what is the total in millions of expected cash outflow to satisfy contractual obligations and commitments as of december 31 , 2007? |
| 376 | `finqa:test:ETR/2004/page_239.pdf-4` | `multi_2_step` | 2 | yes | what is the increase in operation and maintenance expenses as a percentage of net revenue in 2003? |
| 377 | `finqa:test:PNC/2014/page_111.pdf-2` | `single_subtract` | 1 |  | for equity investment balances including unfunded commitments what was the change in millions between december 31 , 2014 and december 31 , 2013/ |
| 378 | `finqa:test:SYY/2006/page_71.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in total rental expense under operating leases from july 1 , 2006 to july 2 , 2007? |
| 379 | `finqa:test:BLL/2012/page_31.pdf-2` | `multi_2_step` | 2 |  | what is the roi of an investment in dj us containers & packaging from 2007 to 2012? |
| 380 | `finqa:test:MKTX/2012/page_42.pdf-1` | `multi_2_step` | 2 |  | by how much did the high of mktx stock increase from 2011 to march 2012? |
| 381 | `finqa:test:STT/2011/page_69.pdf-4` | `single_divide` | 1 | yes | what percentage of restructuring cost comes from employee-related costs? |
| 382 | `finqa:test:ABMD/2005/page_29.pdf-2` | `comparison` | 1 |  | did compensation expense related to the company 2019s employee stock purchase plan grow from 2004 to 2005? |
| 383 | `finqa:test:UNP/2016/page_52.pdf-2` | `single_divide` | 1 |  | in 2015 what was the percent of the total operating revenue that was from chemical freight |
| 384 | `finqa:test:MRK/2013/page_3.pdf-2` | `multi_2_step` | 2 |  | what is the growth rate in total sales in 2012? |
| 385 | `finqa:test:GPN/2010/page_89.pdf-2` | `single_multiply` | 1 | yes | what is the total fair value of non-vested shares as of may 31 , 2010? |
| 386 | `finqa:test:ANSS/2016/page_47.pdf-2` | `single_divide` | 1 |  | what is the proportion of total global headquarters leases to total other operating leases? |
| 387 | `finqa:test:BLK/2012/page_145.pdf-3` | `multi_3_step` | 3 |  | what portion of the total long-term borrowings is due in the next 36 months? |
| 388 | `finqa:test:WRK/2018/page_107.pdf-4` | `multi_4_step` | 4 |  | what percent would the balance by the end of 2018 increase if the unrecognized tax benefits were included? |
| 389 | `finqa:test:INTC/2013/page_31.pdf-4` | `multi_2_step` | 2 | yes | what was the percent of the increase in the dow jones u.s . technology index from 2011 to 2012 |
| 390 | `finqa:test:C/2018/page_176.pdf-2` | `single_multiply` | 1 | yes | what was the value of the shares granted |
| 391 | `finqa:test:GS/2014/page_165.pdf-1` | `single_divide` | 1 |  | what percentage of total other liabilities and accrued expenses in 2013 are due to compensation and benefits? |
| 392 | `finqa:test:AMT/2014/page_149.pdf-2` | `single_add` | 1 |  | what would 2014 contingent consideration be without the foreign currency translation adjustment , in millions? |
| 393 | `finqa:test:MRO/2003/page_45.pdf-3` | `multi_2_step` | 2 |  | what was map's 3 year growth of gasoline production? |
| 394 | `finqa:test:ECL/2016/page_52.pdf-2` | `single_divide` | 1 |  | what percentage of long-term debt is current debt? |
| 395 | `finqa:test:TMUS/2017/page_29.pdf-2` | `single_divide` | 1 |  | what is the average size ( in square feet ) of call centers in 2017? |
| 396 | `finqa:test:JPM/2018/page_90.pdf-1` | `single_divide` | 1 |  | in 2018 what was the percent of the cib markets net interest income as part of the managed interest income |
| 397 | `finqa:test:ETR/2015/page_17.pdf-4` | `multi_2_step` | 2 | yes | in october 2015 , what was the ratio of the entergy recorded a regulatory liability to the tax liability |
| 398 | `finqa:test:GS/2013/page_85.pdf-2` | `multi_2_step` | 2 |  | as of december 2013 and december 2012 , what was the average fair value of the securities and certain overnight cash deposits included in gce , in billions? |
| 399 | `finqa:test:MSI/2008/page_69.pdf-1` | `multi_4_step` | 4 |  | what percentage difference of consolidated net sales from 2006 to 2008? |
| 400 | `finqa:test:GS/2015/page_188.pdf-4` | `single_add` | 1 |  | in billions , what was the total for 2015 and 2014 relating to commitments to invest in funds managed by the firm? |
| 401 | `finqa:test:AWK/2012/page_117.pdf-2` | `multi_2_step` | 2 |  | by how much did changes in the company 2019s gross liability increase from 2011 to 2012? |
| 402 | `finqa:test:MO/2014/page_62.pdf-2` | `single_divide` | 1 |  | what is the restricted stock and deferred stock vested in 2014 as a percentage of net earnings attributable to altria group inc . in 2014? |
| 403 | `finqa:test:IP/2009/page_84.pdf-3` | `single_divide` | 1 |  | at december 31 , 2009 , total future minimum commitments under existing non-cancelable leases and purchase obligations what was the percent of the lease obligations compared to the purchase obligations in 2012 |
| 404 | `finqa:test:VNO/2014/page_57.pdf-2` | `single_subtract` | 1 | yes | what was the five year change in the s&p 500 index? |
| 405 | `finqa:test:BKNG/2016/page_33.pdf-3` | `multi_5_step` | 5 |  | what was the difference in percentage change in priceline group and the s&p 500 index for the five year period ended 2016? |
| 406 | `finqa:test:BLL/2010/page_37.pdf-4` | `single_add` | 1 |  | without the charge for the a/r securitization , what would cash flows provided by operating activities for all operations in 2010 have been ( in millions ) ? |
| 407 | `finqa:test:D/2002/page_87.pdf-3` | `multi_2_step` | 2 |  | what is the growth rate in rental expense included in other operations and maintenance expense in 2002 compare to 2001? |
| 408 | `finqa:test:AMT/2012/page_50.pdf-2` | `single_multiply` | 1 |  | was was the total amount spent on stock repurchases in december 2012? |
| 409 | `finqa:test:BLL/2011/page_32.pdf-2` | `table_average` | 1 |  | what were average net sales in millions for the three years ending in 2011? |
| 410 | `finqa:test:ADBE/2008/page_74.pdf-1` | `single_divide` | 1 |  | what is the yearly amortization rate for the purchased technology? |
| 411 | `finqa:test:AMT/2012/page_118.pdf-2` | `single_divide` | 1 |  | pursuant to the agreement , on march 30 , 2012 , what was the approximate price for each site the company purchased in thousands |
| 412 | `finqa:test:AON/2007/page_188.pdf-1` | `multi_2_step` | 2 |  | what is the percentual increase in the balance during the year 2007? |
| 413 | `finqa:test:HIG/2004/page_140.pdf-3` | `single_add` | 1 |  | what is the change in net income from cumulative effect of adoption? |
| 414 | `finqa:test:MRO/2013/page_39.pdf-1` | `comparison` | 1 |  | in 2013 , was the percentage of our u.s . crude oil and condensate production that was sweet higher than 2012 ? |
| 415 | `finqa:test:PPG/2006/page_42.pdf-2` | `single_divide` | 1 |  | what was the increase in asset retirement obligations for closure of assets in the chemicals manufacturing process in 2006? |
| 416 | `finqa:test:CMCSA/2008/page_36.pdf-1` | `single_divide` | 1 |  | scalable infrastructure represents what percent of capital expenditures incurred the cable segment during 2007? |
| 417 | `finqa:test:AAPL/2006/page_131.pdf-1` | `single_add` | 1 |  | if mr . oppenheimer's rsus vest , how many total shares would he then have? |
| 418 | `finqa:test:AON/2018/page_87.pdf-2` | `single_subtract` | 1 |  | what is the decrease observed in the additions for tax positions of prior years , in millions? |
| 419 | `finqa:test:DVN/2012/page_77.pdf-2` | `multi_2_step` | 2 |  | what percentage of total debt maturity occurred in 2018 and thereafter? |
| 420 | `finqa:test:ANET/2015/page_156.pdf-2` | `single_divide` | 1 |  | what is the current portion of the present value of lease obligations? |
| 421 | `finqa:test:IPG/2008/page_72.pdf-3` | `multi_3_step` | 3 |  | what is the percentage increase from beginning to end of 2008 in unrecognized tax benefits? |
| 422 | `finqa:test:CMCSA/2008/page_36.pdf-3` | `single_divide` | 1 |  | what was the percent of the capital expenditures we incurred in our cable segment in 2006 for the customer premise equipment |
| 423 | `finqa:test:ALLE/2015/page_24.pdf-2` | `single_subtract` | 1 |  | considering the year 2014 , what are the variation between the expenses for environmental remediation at sites and the reserves environmental matters , in millions? |
| 424 | `finqa:test:C/2008/page_65.pdf-3` | `multi_2_step` | 2 |  | what was the percentage change in total managed consumer loans from 2006 to 2007? |
| 425 | `finqa:test:NKE/2009/page_43.pdf-2` | `multi_2_step` | 2 | yes | what percent of the total amount outstanding is due to notes payable due at mutually agreed-upon dates within one year of issuance or on demand? |
| 426 | `finqa:test:ETR/2004/page_239.pdf-1` | `single_divide` | 1 | yes | what is the decrease in gross wholesale revenue as a percentage of 2003 net revenue? |
| 427 | `finqa:test:CME/2017/page_40.pdf-4` | `comparison` | 1 |  | did the cme group outperform the s&p 500 over 5 years? |
| 428 | `finqa:test:SNA/2013/page_34.pdf-3` | `multi_2_step` | 2 |  | what is the return on investment if $ 100 are invested in snap-on at the end of 2008 and sold at the end of 2010? |
| 429 | `finqa:test:GS/2018/page_78.pdf-3` | `multi_2_step` | 2 |  | what are the pre-tax earnings in 2016 , in billions? |
| 430 | `finqa:test:CDW/2017/page_38.pdf-2` | `single_divide` | 1 | yes | what was 2016 gross margin percent? |
| 431 | `finqa:test:DRE/2005/page_30.pdf-2` | `single_add` | 1 |  | what was the total gain on sales in 2004 before any adjustment for impairments in millions |
| 432 | `finqa:test:MMM/2007/page_84.pdf-1` | `single_divide` | 1 |  | what is the ratio of the respirator mask/asbestos receivables to respirator mask/asbestos liabilities in 2007 |
| 433 | `finqa:test:NWS/2017/page_119.pdf-2` | `single_divide` | 1 |  | what percentage of the intangible assets is related to the license of the realtor.com ae trademark? |
| 434 | `finqa:test:HII/2015/page_121.pdf-4` | `single_divide` | 1 |  | what was the operating margin in the 4th quarter |
| 435 | `finqa:test:HOLX/2009/page_151.pdf-2` | `single_multiply` | 1 | yes | what is the total fair value of non-vested shares as of september 27 , 2008? |
| 436 | `finqa:test:ANSS/2012/page_93.pdf-3` | `single_subtract` | 1 |  | what is the range , in thousands , for united states' revenue from 2010-2012? |
| 437 | `finqa:test:AWK/2013/page_122.pdf-1` | `single_add` | 1 |  | what is the he company 2019s gross liability at the end of 2013 if including interest and penalties? |
| 438 | `finqa:test:C/2009/page_63.pdf-2` | `single_divide` | 1 |  | what percent of total contractual obligations in 2010 are made up of long-term debt obligations? |
| 439 | `finqa:test:AMT/2012/page_118.pdf-4` | `multi_4_step` | 4 |  | for the vivo acquisition how many of the allowed towers were actually purchased under the final amended purchase agreement? |
| 440 | `finqa:test:GRMN/2006/page_68.pdf-1` | `single_subtract` | 1 | yes | what is the decrease observed in the operating leases with payments due to 3-5 years and payments due to more than 5 years? |
| 441 | `finqa:test:MRO/2003/page_45.pdf-2` | `table_sum` | 1 |  | what were total distillates sales in millions for the three year period ? 365 346 345 |
| 442 | `finqa:test:AMT/2014/page_160.pdf-1` | `multi_2_step` | 2 |  | what is the percentage change in aggregate rent expense from 2013 to 2014? |
| 443 | `finqa:test:CDW/2015/page_93.pdf-1` | `multi_3_step` | 3 |  | what was the average amount expensed by the company for the company contributions to the profit sharing and other savings plans from 2013 to 2015 in millions |
| 444 | `finqa:test:LMT/2012/page_73.pdf-3` | `multi_2_step` | 2 |  | what is the percentage change in the weighted average common shares outstanding for basic computations from 2010 to 2011? |
| 445 | `finqa:test:DXC/2018/page_56.pdf-1` | `single_divide` | 1 | yes | in fiscal 2018 what percentage of total costs and expenses was costs of services ( excludes depreciation and amortization and restructuring costs ) ? |
| 446 | `finqa:test:CME/2010/page_123.pdf-1` | `single_divide` | 1 |  | whats is the percentage of equity compensation plans that were not approved by security holders? |
| 447 | `finqa:test:STT/2007/page_111.pdf-4` | `single_subtract` | 1 |  | what is the percent change in indemnified securities financing between 2006 and 2007? |
| 448 | `finqa:test:AAL/2013/page_172.pdf-3` | `single_divide` | 1 |  | what is the percent of americans labor-related deemed claim as a part of the total claims and other bankruptcy settlement obligations as of december2013 |
| 449 | `finqa:test:IPG/2006/page_77.pdf-3` | `multi_2_step` | 2 |  | what percent increase in long-term debt did the floating rate notes maturing in 2010? |
| 450 | `finqa:test:AON/2015/page_96.pdf-1` | `single_add` | 1 |  | what was the average number of shares issued to employees from 2013 to 2015 |
| 451 | `finqa:test:ADI/2010/page_80.pdf-2` | `multi_2_step` | 2 |  | what is the growth rate in the balance of mutual funds in 2010? |
| 452 | `finqa:test:ADI/2019/page_29.pdf-3` | `multi_2_step` | 2 |  | in 2008 , how much percent did the board of directors increase the share repurchase program . |
| 453 | `finqa:test:ALXN/2016/page_153.pdf-2` | `single_divide` | 1 |  | what is the borrowing under the term loan facility as a percentage of the total contractual maturities of long-term debt obligations due subsequent to december 31 , 2016? |
| 454 | `finqa:test:AMT/2012/page_50.pdf-1` | `single_divide` | 1 |  | for the quarter december 31 , 2012 what was the percent of the total number of shares purchased in december |
| 455 | `finqa:test:UPS/2010/page_52.pdf-2` | `single_divide` | 1 |  | what percentage of total expected cash outflow to satisfy contractual obligations and commitments as of december 31 , 2010 are due in 2013? |
| 456 | `finqa:test:PNC/2008/page_122.pdf-2` | `table_average` | 1 | yes | for 2008 across the three categories , what were the average mount of liabilities in millions? |
| 457 | `finqa:test:SLG/2011/page_91.pdf-3` | `table_sum` | 1 |  | what was the total number of shares vested during the three year period? |
| 458 | `finqa:test:STT/2006/page_95.pdf-4` | `multi_2_step` | 2 |  | what is the growth rate in the average price of repurchased shares from 2005 to 2006? |
| 459 | `finqa:test:HWM/2015/page_173.pdf-1` | `multi_2_step` | 2 |  | how bigger were the interest and penalties concerning the interest income in the year 2015? |
| 460 | `finqa:test:MSI/2008/page_69.pdf-2` | `multi_2_step` | 2 |  | what was the percentage decline in the operating loss from 2007 to 2008 |
| 461 | `finqa:test:JPM/2014/page_122.pdf-1` | `multi_2_step` | 2 |  | what was the percentage change in loans retained from 2013 to 2014? |
| 462 | `finqa:test:C/2009/page_197.pdf-1` | `multi_2_step` | 2 |  | what was the tax rate applied applied to the goodwill impairment charge in the fourth quarter of 2008 |
| 463 | `finqa:test:BLL/2010/page_35.pdf-2` | `multi_2_step` | 2 |  | what was the percentage change in net sales for the discontinued operations between 2009 and 2010? |
| 464 | `finqa:test:MAR/2004/page_45.pdf-1` | `single_subtract` | 1 |  | what is the difference of between the carrying amount and the fair value of notes and other long-term assets in 2004? |
| 465 | `finqa:test:FIS/2017/page_64.pdf-4` | `single_divide` | 1 |  | what percent of the total increase or decrease would the euro be in 2017? |
| 466 | `finqa:test:AON/2007/page_175.pdf-1` | `multi_2_step` | 2 |  | what is the net change in aon 2019s unpaid restructuring liabilities during 2007? |
| 467 | `finqa:test:AAPL/2003/page_48.pdf-1` | `single_subtract` | 1 | yes | excluding accretion , what was the ending balance of asset retirement liability as of september 27 2003 , in millions? |
| 468 | `finqa:test:LMT/2016/page_49.pdf-4` | `table_average` | 1 |  | what were average operating profit for mfc in millions between 2014 and 2016? |
| 469 | `finqa:test:PNC/2015/page_93.pdf-1` | `single_divide` | 1 |  | for interest only products , what percent of the total was due in 2020 and thereafter? |
| 470 | `finqa:test:MAS/2017/page_27.pdf-2` | `multi_5_step` | 5 |  | what was the difference in percentage cumulative total shareholder return on masco common stock versus the s&p 500 index for the five year period ended 2017? |
| 471 | `finqa:test:AMT/2014/page_160.pdf-2` | `single_divide` | 1 |  | what portion of future lease payments are due after 5 years? |
| 472 | `finqa:test:GPN/2014/page_92.pdf-2` | `multi_2_step` | 2 |  | what is the total value of securities approved by security holders but net yer issued , ( in millions ) ? |
| 473 | `finqa:test:BLL/2006/page_67.pdf-1` | `single_add` | 1 |  | current assets were what percent of net assets acquired for the can and alcan transactions? |
| 474 | `finqa:test:CME/2017/page_40.pdf-2` | `contains_exp` | 5 | yes | what is the anualized return for s&p 500 from 2012 to 2017? |
| 475 | `finqa:test:JPM/2012/page_140.pdf-2` | `multi_2_step` | 2 | yes | what was the percentage change in loans retained from 2011 to 2012? |
| 476 | `finqa:test:PM/2017/page_32.pdf-2` | `multi_2_step` | 2 | yes | what is the change in basis points of the rate of postretirement plans from 2016 to 2017? |
| 477 | `finqa:test:MRO/2017/page_96.pdf-2` | `single_subtract` | 1 |  | what is the difference in the initial health care trend rate and the ultimate health care trend rate in 2017? |
| 478 | `finqa:test:GS/2012/page_121.pdf-2` | `multi_2_step` | 2 |  | what is the percentage change in total financial liabilities at fair value in 2012? |
| 479 | `finqa:test:ETR/2011/page_301.pdf-2` | `single_subtract` | 1 |  | by how much did the receivables from the money pool differ from 2009 to 2010? |
| 480 | `finqa:test:GS/2012/page_142.pdf-2` | `table_max` | 1 |  | in millions for 2012 2011 , what was maximum collateral posted? |
| 481 | `finqa:test:IP/2006/page_38.pdf-3` | `single_divide` | 1 | yes | what was the percentage of total debt associated with lease obligations related to discontinued operations and businesses held for sale due in 2007 |
| 482 | `finqa:test:ECL/2017/page_79.pdf-1` | `multi_2_step` | 2 |  | what portion of total assets acquired of anios are intangible assets? |
| 483 | `finqa:test:ADBE/1999/page_64.pdf-2` | `single_divide` | 1 | yes | what portion of the 1999 accrual balance related to restructurings is comprised of canceled contracts? |
| 484 | `finqa:test:JPM/2003/page_106.pdf-3` | `table_average` | 1 | yes | what was the average value of structured commercial loan vehicles issued by vies in 2002 and 2003 , in billions? |
| 485 | `finqa:test:AES/2010/page_227.pdf-2` | `single_divide` | 1 |  | what percentage of recourse debt as of december 31 , 2010 matures in 2015? |
| 486 | `finqa:test:LMT/2014/page_50.pdf-3` | `single_subtract` | 1 |  | what was the difference in operating margin between 2012 and 2013? |
| 487 | `finqa:test:AAL/2013/page_172.pdf-4` | `single_divide` | 1 | yes | what portion of the total bankruptcy settlement obligations are related to single-dip equity obligations? |
| 488 | `finqa:test:LMT/2016/page_49.pdf-2` | `single_subtract` | 1 |  | what are the total operating expenses for 2016? |
| 489 | `finqa:test:ADBE/1999/page_64.pdf-3` | `single_subtract` | 1 |  | what is the net change in the balance of accrual related to restructurings during 1999? |
| 490 | `finqa:test:HST/2018/page_135.pdf-1` | `single_subtract` | 1 |  | what was the change in million of the unrecognized tax benefits between 2017 and 2018? |
| 491 | `finqa:test:DG/2005/page_44.pdf-2` | `multi_2_step` | 2 |  | what was the total impairment costs recorded from 2003 to 2005 in millions |
| 492 | `finqa:test:BLL/2011/page_32.pdf-3` | `multi_2_step` | 2 |  | the contracted backlog at december 31 , 2011 contained how much in million dollars for fixed price contracts? |
| 493 | `finqa:test:GPN/2010/page_87.pdf-2` | `multi_4_step` | 4 |  | what is the percentage change in the after-tax share-based compensation cost from 2009 to 2010? |
| 494 | `finqa:test:FIS/2006/page_31.pdf-2` | `multi_2_step` | 2 | yes | what portion of the total leased locations are located in united states? |
| 495 | `finqa:test:CME/2010/page_123.pdf-4` | `single_divide` | 1 |  | what percentage of the outstanding options were from plans approved by security holders? |
| 496 | `finqa:test:ABMD/2006/page_43.pdf-3` | `single_divide` | 1 |  | what percentage of total obligations are operating lease obligations in 2008? |
| 497 | `finqa:test:SNA/2007/page_49.pdf-1` | `multi_3_step` | 3 | yes | what was the average cash flow provided from operating activities from 2005 to to 2007 $ 231.1 million in 2007 , $ 203.4 million in 2006 , and $ 221.1 million in 2005 . |
| 498 | `finqa:test:TFX/2017/page_78.pdf-2` | `multi_2_step` | 2 |  | what portion of the total number of securities approved by security holders remains available for future issuance? |
| 499 | `finqa:test:AES/2002/page_128.pdf-3` | `single_divide` | 1 |  | what percentage of total future minimum lease commitments is due in 2003? |
| 500 | `finqa:test:RSG/2018/page_135.pdf-1` | `single_divide` | 1 |  | based on the december 31 2018 target what was the debt to equity ratio |
