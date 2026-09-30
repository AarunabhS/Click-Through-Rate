import numpy as np
import pandas as pd
import predict
from analysis import CATEGORICAL


def test_batch_csv_preserves_identifier_strings_and_missing_categories(tmp_path,monkeypatch):
    frame=pd.DataFrame({'depth':[3,3],'position':[1,1],**{name:['000123',None] for name in CATEGORICAL}})
    source=tmp_path/'new_rows.csv'
    frame.to_csv(source,index=False)
    class Model:
        def predict_proba(self,X):
            assert X.ad_id.iloc[0]=='000123'
            assert pd.isna(X.ad_id.iloc[1])
            return np.array([[.9,.1],[.8,.2]])
    monkeypatch.setattr(predict.joblib,'load',lambda path:{'model':Model(),'threshold':.5})
    result=predict.predict(source,tmp_path/'model.joblib',tmp_path/'predictions.csv')
    assert result.predicted.tolist()==[0,0]
