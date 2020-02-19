# Hospital Vital Indicators Dashboard for NGOs

## Background
Our objective was to produce a dashboard that enables NGOs to easily look up the status and needs of hospitals in Venezuela. This helps NGOs decide what hospitals to target, and what their greatest needs are. The dashboard gives a high-level overview of hospital status across a few key categories: medical supplies, operability, water, power, and nutritional availability.

To accomplish this, we created a Python data cleaning script, and a Tableau dashboard. The Python script cleans and prepares the DFH survey data, and outputs a CSV file for use in Tableau. Also, we created lookup table file with all the information about the hospitals, by code and state.

## Data Quality Issues
As the initial analysis on the dataset showed, C4V can improve the quality of its information, by doing some changes in the google form.

Question #4: "Ente Administrativo"
There is only five options allowed multiple selections. The suggestion is to have all the possible regions as fields, as
they already exists in Question 2.

Question #48: "Power Outage Number by Day"
In the survey, manual input for number. The suggestion is to have a single selection field rather than a multiple selection field 
Allowed answers: Yes | No | No, Yes

Question #49: "Power Outage Number by Day"
In the survey, manual input for number. The suggestion is to have a drop drown list rather than a typed field

Question #53: "Equipment Names"
In the survey, manual input for equipments' names. The suggestion is to have a drop drown list rather than a typed field

## Data cleaning script
Run data cleaning by executing the Python script:

<h3 style="text-align: center;"><span style="color: #333399;"><a style="color: #333399;" href="https://github.com/Jorgebt/Code4Venezuela_NGOs_Dashboard/blob/master/clean_survey_data.py">clean_survey_data.py</a></span></h3>
This outputs the file "cleaned_survey_dataset.csv".

Cleaning operations:
- Created an extra string column with the report week, formatted as "[Year]-[Week of Year]". This allows for sorting the data in report week order.
- De-duplicated the reports by only using the latest submitted report by hospital and week.
- Created a corresponding numeric (ordinal) column for each of the medicine supply fields. Also calculate an aggregated rating of medical supplies.
  - Similarly, created a corresponding numeric column for each of the operability fields.
  
  <h2 style="text-align: center;">Authors</h2>
 Lizaveta Radzevich, Luis Rodas, Jorge Betancourt, Pedro Nascimento, Ethan Yung
