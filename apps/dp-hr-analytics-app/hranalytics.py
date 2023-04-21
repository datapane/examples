import pandas as pd
import altair as alt
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.feature_selection import RFE
from sklearn.preprocessing import MinMaxScaler
from scipy import stats

def preprocess_data(data):
    # Preprocess the data: drop unnecessary columns, handle missing values, and convert categorical variables
    data = data.drop(columns=['Employee_Name', 'EmpID', 'DOB', 'DateofHire', 'DateofTermination', 'LastPerformanceReview_Date'])
    data['HispanicLatino'] = data['HispanicLatino'].apply(lambda x: 1 if x.lower() == 'yes' else 0)
    data = pd.get_dummies(data, columns=['Position', 'State', 'Sex', 'MaritalDesc', 'CitizenDesc', 'RaceDesc', 'TermReason', 'EmploymentStatus', 'Department', 'ManagerName', 'RecruitmentSource', 'PerformanceScore'])
    
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    data = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)
    
    return data

def benchmark_employee(data, employee_name, benchmark_features=None):
    if benchmark_features is None:
        benchmark_features = ['Salary', 'EngagementSurvey', 'EmpSatisfaction', 'SpecialProjectsCount']

    # Check if the employee name exists in the dataset
    if employee_name not in data['Employee_Name'].values:
        raise ValueError("Employee name not found in the dataset.")

    # Extract the employee's data
    employee_data = data.loc[data['Employee_Name'] == employee_name, benchmark_features].squeeze()

    # Calculate the average values of the benchmark features for all employees
    mean_values = data[benchmark_features].mean()

    # Calculate the percentiles of the employee's values compared to their peers
    percentiles = data[benchmark_features].apply(lambda x: stats.percentileofscore(x, employee_data[x.name]))

    # Combine the employee's data, mean values, and percentiles into a single DataFrame
    benchmark_df = pd.DataFrame({'Feature': benchmark_features,
                                 'Employee Value': employee_data.values,
                                 'Average Value': mean_values.values,
                                 'Percentile': percentiles.values})

    return benchmark_df

def predict_employee_attrition(data, top_n_percent=10):
    # Save employee names before preprocessing
    employee_names = data['Employee_Name']
    
    # Preprocess the data
    data = preprocess_data(data)
    
    # Separate features and target variable
    X = data.drop('Termd', axis=1)
    y = data['Termd'].astype(int)  # Convert the target variable to int
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Standardize the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train a Random Forest Classifier
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    
    # Make predictions for the still employed employees
    still_employed = data[data['Termd'] == 0]
    still_employed_index = still_employed.index
    X_still_employed = X.loc[still_employed_index]
    
    # Calculate the probability of attrition
    attrition_probabilities = model.predict_proba(X_still_employed)[:, 1]
    
    # Create a DataFrame with employee names and their attrition probabilities
    at_risk_employees = pd.DataFrame({'Employee_Name': employee_names.loc[still_employed_index],
                                      'Attrition_Probability': attrition_probabilities})
    
    # Calculate the number of employees to return based on the top_n_percent parameter
    top_n = int(len(at_risk_employees) * top_n_percent / 100)
    
    # Sort the employees by their attrition probability and return the top N
    top_at_risk_employees = at_risk_employees.nlargest(top_n, 'Attrition_Probability')
    
    return top_at_risk_employees

    
def key_drivers_of_attrition(data, top_n=20):
    # Preprocess the data
    data = preprocess_data(data)
    
    # Separate features and target variable
    X = data.drop('Termd', axis=1)
    y = data['Termd'].astype(int)  # Convert the target variable to int
    
    # Perform feature selection using Random Forest
    model = RandomForestClassifier(random_state=42)
    model.fit(X, y)
    feature_importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({'Features': X.columns, 'Importance': feature_importances})
    
    # List of features to exclude (leaky features)
    exclude_features = ['EmploymentStatus_', 'TermReason_', 'IsTerminated', 'EmpStatusID']
    
    # Filter out the leaky features
    feature_importance_df = feature_importance_df[~feature_importance_df['Features'].str.startswith(tuple(exclude_features))]
    
    # Get the top N features
    top_features = feature_importance_df.nlargest(top_n, 'Importance')
    
    # Scale the importance values to the range of 0 to 100
    scaler = MinMaxScaler(feature_range=(0, 100))
    top_features['ScaledImportance'] = scaler.fit_transform(top_features[['Importance']])
    
    return top_features


def total_employees(data):
    return data.shape[0]

def average_salary(data):
    return data["Salary"].mean()

def gender_diversity(data):
    male_count = data[data["Sex"] == "M"].shape[0]
    return male_count / total_employees(data) * 100

def turnover_rate(data):
    term_count = data[data["Termd"] == 1].shape[0]
    return term_count / total_employees(data) * 100

def average_employee_satisfaction(data):
    return data["EmpSatisfaction"].mean()

def plot_salary_distribution(data):
    chart = alt.Chart(data).mark_bar().encode(
        alt.X("Salary:Q", bin=alt.Bin(maxbins=30), title='Salary'),
        y='count()'
    ).properties(title='Salary Distribution')
    return chart

def plot_employees_by_dept(data):
    chart = alt.Chart(data).mark_bar().encode(
        x='Department:N',
        y='count()',
        color='Department:N'
    ).properties(title='Number of Employees by Department')
    return chart

def plot_gender_distribution(data):
    chart = alt.Chart(data).mark_bar().encode(
        x='Sex:N',
        y='count()',
        color='Sex:N'
    ).properties(title='Gender Distribution')
    return chart

def plot_performance_by_department(data):
    chart = alt.Chart(data).mark_bar().encode(
        x='Department:N',
        y='average(PerfScoreID):Q',
        color='Department:N'
    ).properties(title='Average Performance Score by Department')
    return chart

def plot_employee_satisfaction(data):
    chart = alt.Chart(data).mark_bar().encode(
        x='EmpSatisfaction:N',
        y='count()',
        color='EmpSatisfaction:N'
    ).properties(title='Employee Satisfaction Distribution')
    return chart