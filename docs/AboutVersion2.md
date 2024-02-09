![alt text](./images/header_logo.png)


#### HebSafeHarbor - CLALIT Validation  
# Version 2

## Contents
 - [Disadvantages of the previous version](#disadvantages-of-the-previous-version) 
 - [Changes](#changes) 
 - [Improvements](#improvements)
 - [Examples](#examples)
 - [Accuracy metrics](#accuracy-metrics)
 
 ## Disadvantages of the previous version  
 - Over anonymization of medical concepts and clinical descriptions.  
 - Incomplete anonymization of Ethiopian names.  
 - Incomplete anonymization of dates and times in certain formats.  
 - Permanent anonymization rules without reference to the world of medical content.
 
 ## Changes  
 - Expansion of lexicons.
 - Shifting/anonymizing dates according to user's need, With the option to use a custom function.
 - Using a model that allows better identification of special names (mainly Ethiopians).
 - Anonymization by domain(context).

## Improvements  
- False Positive Rate(FPR) dropped from 23.3% to 17.9%, a 5.4% improvement, mainly thanks to the new approach for spacial names and ambiguous cities.    
- True Positive Rate(TPR) rose from 76.7% to 82.1%, an increase of 5.4%. This can be attributed to the decrease of the FPR percentage and anonymizing special names and ids.  
- FN cases per file dropped from 2.314 to 1.303, a 1.011 improvement.
 
 ## Examples  
Original text:  
  
![original](./images/lexicons_improve_1245002453676_original.png)  
  
Anonymized text:  
    
![original](./images/lexicons_improve_1245002453676_encrypt.png)  
 
 ## Accuracy metrics
 The performance measurement is based on a batch of 500 ***chest CT tests***, including 780 free texts.  
 
|Version| Average FPR | Average TPR | Average FN cases per file |
| :---: | :---: | :---: | :---: |
|Original| 0.451 | 0.549 | 2.335 |
|Version 1| 0.233 | 0.767 | 2.314 |  
|**Version 2**| **0.179** | **0.821** | **1.303** |
  
An example of a true positive(TP):   

| Original Text | Anonymization |
| :---: | :---: |
|&#x202b; נבדק: ישראל ישראלי ת"ז: 123456789|&#x202b; נבדק: **<שם_>** ת"ז: **<מזהה_>**|  



An example of a false positive(FP):  
 
| Original Text | Anonymization |
| :---: | :---: |
|&#x202b; לא הודגם תפליט פלאורלי או פריקרדיאלי.|&#x202b; לא הודגם **<ארגון_>** פלאורלי או פריקרדיאלי.|  


An example of a false negative(FN):  

| Original Text | Anonymization |
| :---: | :---: |
|&#x202b; נבדק: ישראל בן ישראלי ת"ז: 123456789|&#x202b; נבדק: **ישראל בן ישראלי** ת"ז: **<מזהה_>**|  

<br />
<br />
<br />
   
![alt text](./images/Israel_Innovation_Authority.svg.png)
