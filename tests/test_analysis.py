import numpy as np
import pandas as pd
import pytest
from analysis import CATEGORICAL, load_data, prepare_features, preprocessing
from workflow import make_splits


def example():
    frame=pd.DataFrame({k:[str(i%8) for i in range(120)] for k in CATEGORICAL})
    frame["depth"]=3
    frame["position"]=np.arange(120)%3+1
    frame["click"]=[0,1]*60
    frame["user_id"]=np.repeat(np.arange(1,61),2).astype(str)
    frame["impression"]=1
    frame["click_time"]="after_the_event"
    frame["view_count"]=frame.click
    return frame


def test_post_event_columns_and_identifiers_are_excluded():
    X=prepare_features(example())
    assert set(X)=={"depth","position",*CATEGORICAL}
    assert "click" not in X and "impression" not in X and "view_count" not in X


def test_known_users_are_isolated_and_new_ads_supported(tmp_path):
    p=tmp_path/"click.csv"
    example().to_csv(p,index=False)
    X,y,groups,_=load_data(p)
    splits=make_splits(y,groups)
    assert not set(groups.iloc[splits["train"]]) & set(groups.iloc[splits["test"]])
    pipeline=preprocessing().fit(X.iloc[splits["train"]])
    result=pipeline.transform(X.iloc[splits["test"]].assign(ad_id="unseen_ad"))
    assert result.shape[0]==len(splits["test"])


def test_ad_position_cannot_exceed_depth():
    frame=example()
    frame.loc[0,"position"]=4
    with pytest.raises(ValueError,match="position"):
        prepare_features(frame)
