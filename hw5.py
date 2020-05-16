
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pathlib
from pathlib import Path
from typing import Union, Tuple

class QuestionnaireAnalysis:
    """
    Reads and analyzes data generated by the questionnaire experiment.
    Should be able to accept strings and pathlib.Path objects.
    """

    def __init__(self, data_fname: Union[pathlib.Path, str]):
        self.data_fname=pathlib.Path(data_fname).resolve()
        if not self.data_fname.exists():
            raise ValueError("file does not exist")
        # ...

    def read_data(self):
        """Reads the json data located in self.data_fname into memory, to
        the attribute self.data.
        """
        self.data=pd.read_json(self.data_fname)
        # ...

    def show_age_distrib(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calculates and plots the age distribution of the participants.

    Returns
    -------
    hist : np.ndarray
      Number of people in a given bin
    bins : np.ndarray
      Bin edges
        """
        df=self.data
        df2=df['age']
        df3=df2.to_numpy()
        x =df3[~np.isnan(df3)]
        hist1=np.histogram(x, bins=[0,10,20,30,40,50,60,70,80,90,100])
        return hist1

    def remove_rows_without_mail(self) -> pd.DataFrame:
        """Checks self.data for rows with invalid emails, and removes them.

    Returns
    -------
    df : pd.DataFrame
      A corrected DataFrame, i.e. the same table but with the erroneous rows removed and
      the (ordinal) index after a reset.
        """
        df=self.data
        email_data=df['email'].to_list()
        x=[] 
        for order in email_data:
            splitemail = order.split('@')
            emailstr = '.'.join(splitemail)
            splitemail2 = emailstr.split('.')
            if len(splitemail2)==3:
                for i in splitemail2:
                    if i.isalnum()==False:
                        x.append(order)
                        break
            elif len(splitemail2)!=3:
                x.append(order)
            for emailName in x:
                df = df[df.email != emailName].reset_index(drop=True)
        return df

    def fill_na_with_mean(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Finds, in the original DataFrame, the subjects that didn't answer
        all questions, and replaces that missing value with the mean of the
        other grades for that student.

    Returns
    -------
    df : pd.DataFrame
      The corrected DataFrame after insertion of the mean grade
    arr : np.ndarray
          Row indices of the students that their new grades were generated
        """
        df=self.data
        t1=[]
        t2=[]
        t3=[]
        t4=[]
        t5=[]
        index1 = list(df['q1'].index[df['q1'].apply(np.isnan)])
        for element in index1:
            t1.append(element)
        index2 = list(df['q2'].index[df['q2'].apply(np.isnan)])
        for element in index2:
            t2.append(element)
        index3 = list(df['q3'].index[df['q3'].apply(np.isnan)])
        for element in index3:
            t3.append(element)
        index4 = list(df['q4'].index[df['q4'].apply(np.isnan)])
        for element in index4:
            t4.append(element)
        index5 = list(df['q5'].index[df['q5'].apply(np.isnan)])

        for element in index5:
            t5.append(element)
        list_indices=np.array(sorted(set(index1+index2+index3+index4+index5)))
        df.loc[index1,'q1']=df.loc[index1,['q2', 'q3','q4','q5']].mean(axis=1)
        df.loc[index2,'q2']=df.loc[index2,['q1', 'q3','q4','q5']].mean(axis=1)
        df.loc[index3,'q3']=df.loc[index3,['q1', 'q2','q4','q5']].mean(axis=1)
        df.loc[index4,'q4']=df.loc[index4,['q1', 'q2','q3','q5']].mean(axis=1)
        df.loc[index5,'q5']=df.loc[index5,['q1', 'q2','q3','q4']].mean(axis=1)

        return  tuple([df,list_indices])


    def score_subjects(self, maximal_nans_per_sub: int = 1) -> pd.DataFrame:
        """Calculates the average score of a subject and adds a new "score" column
        with it.

        If the subject has more than "maximal_nans_per_sub" NaN in his grades, the
        score should be NA. Otherwise, the score is simply the mean of the other grades.
        The datatype of score is UInt8, and the floating point raw numbers should be
        rounded down.

        Parameters
        ----------
        maximal_nans_per_sub : int, optional
            Number of allowed NaNs per subject before giving a NA score.

        Returns
        -------
        pd.DataFrame
            A new DF with a new column - "score".
        """
        df=self.data
        t1=[]
        t2=[]
        t3=[]
        t4=[]
        t5=[]
        index1 = list(df['q1'].index[df['q1'].apply(np.isnan)])
        for element in index1:
            t1.append(element)
        index2 = list(df['q2'].index[df['q2'].apply(np.isnan)])
        for element in index2:
            t2.append(element)
        index3 = list(df['q3'].index[df['q3'].apply(np.isnan)])
        for element in index3:
            t3.append(element)
        index4 = list(df['q4'].index[df['q4'].apply(np.isnan)])
        for element in index4:
            t4.append(element)
        index5 = list(df['q5'].index[df['q5'].apply(np.isnan)])
        for element in index5:
            t5.append(element)
        list_indices=sorted(index1+index2+index3+index4+index5)
        y = []
        for a in list_indices:
            if list_indices.count(a)>maximal_nans_per_sub:
                y.append(a)
        means_of_rows=df.loc[:,['q1', 'q2','q3','q4','q5']].mean(axis=1)
        means_of_rows_floored= np.floor(means_of_rows)
        df['score']=means_of_rows_floored.astype('UInt8')
        df.loc[y,'score']=np.NaN
        return df

    def correlate_gender_age(self) -> pd.DataFrame:
        """Looks for a correlation between the gender of the subject, their age
        and the score for all five questions.

    Returns
    -------
    pd.DataFrame
        A DataFrame with a MultiIndex containing the gender and whether the subject is above
        40 years of age, and the average score in each of the five questions.
    """
        df=self.data
        fill_value=df['age'].mean()
        df['age'].fillna(fill_value,inplace=True)
        c=df.shape
        df_age=df['age']>40
        df['age']=df_age
        df2=df.set_index([pd.Index(np.arange(c[0])),'gender','age'])
        df3=df2.groupby(['gender','age']).mean().drop(columns='id')

        return df3
