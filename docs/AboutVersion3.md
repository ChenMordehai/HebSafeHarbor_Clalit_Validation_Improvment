![alt text](./images/header_logo.png)


#### HebSafeHarbor - CLALIT Validation  
# Version 3

## Contents
 - [Disadvantages of the previous version](#disadvantages-of-the-previous-version) 
 - [Changes](#changes) 
 - [Improvements](#improvements)
 - [Examples](#examples)
 - [Accuracy metrics](#accuracy-metrics)
 
 ## Disadvantages of the Original version  
 - Over anonymization of medical concepts and clinical descriptions.  
 - Incomplete anonymization of dates and times in certain formats.  
 - Permanent anonymization rules without reference to the world of medical content.
 
 ## Changes  
 - Expansion of lexicons.
 - Shifting/anonymizing dates according to user's need, With the option to use a custom function.
 - Anonymization by domain(context).
 - Handling cases of Incomplete anonymization in English terms (mainly names).

 ## Examples  
Original text:  
  
![original](./images/lexicons_improve_1245002453676_original.png)  
  
Anonymized text:  
    
![original](./images/lexicons_improve_1245002453676_encrypt.png)  
 
 ## Accuracy metrics

### C.T
<img src="./images/500_ct_accuracy_v3.png" alt="500_ct_accuracy_v3" width="550"/>  
<br></br>
<img src="./images/comparison_lack_anonymization_500_ct_v3.png" alt="comparison_lack_anonymization_500_ct_v3" width="500"/> 
<img src="./images/comparison_over_anonymization_500_ct_v3.png" alt="comparison_over_anonymization_500_ct_v3" width="350"/> 

### Pathology
<img src="./images/500_ct_accuracy_v3.png" alt="500_pathology_accuracy_v3" width="550"/>  
<br></br>
<img src="./images/comparison_lack_anonymization_500_ct_v3.png" alt="comparison_lack_anonymization_500_pathology_v3" width="500"/> 
<img src="./images/comparison_over_anonymization_500_ct_v3.png" alt="comparison_over_anonymization_500_pathology_v3" width="350"/> 

  
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
