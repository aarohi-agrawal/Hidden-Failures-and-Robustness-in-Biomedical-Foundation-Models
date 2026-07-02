### 1.

case_id: phantom0_002
 
Student A label: soft_mirage  
Student B label:  
Student C label: soft_mirage
 
Why did we disagree?  
No disagreement between Student A and Student C.
 
Final decision:  
soft_mirage
 
Rule added to annotation guide:  
None.


### 2.

case_id: phantom0_012_explicit
 
Student A label: hard_mirage  
Student B label:  
Student C label: hard_mirage
 
Why did we disagree?  
No disagreement between Student A and Student C.
 
Final decision:  
hard_mirage
 
Rule added to annotation guide:  
None.


### 3.

case_id: phantom0_003_explicit
 
Student A label: appropriate_abstention  
Student B label:  
Student C label: appropriate_abstention
 
Why did we disagree?  
No disagreement between Student A and Student C.
 
Final decision:  
appropriate_abstention
 
Rule added to annotation guide:  
None.


### 4.

case_id: phantom0_019
 
Student A label: hard_mirage  
Student B label:  
Student C label: soft_mirage
 
Why did we disagree?  
This response was ambiguous because the model gave a direct answer without describing many scene details. Student C treated it as soft_mirage because the response only gave a count. Student A treated it as hard_mirage because a specific crowd count is a visual quantity that would require image evidence.
 
Final decision:  
hard_mirage
 
Rule added to annotation guide:  
Specific counts, quantities, or measurements should be treated as specific visual details. If a model provides a precise count for an image-dependent question without an image, mark hard_mirage = yes.


### 5.

case_id: phantom0_001
 
Student A label: hard_mirage  
Student B label:  
Student C label: hard_mirage
 
Why did we disagree?  
No disagreement between Student A and Student C.
 
Final decision:  
hard_mirage
 
Rule added to annotation guide:  
None