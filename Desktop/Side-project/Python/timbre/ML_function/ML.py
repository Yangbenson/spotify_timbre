from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.ensemble import BaggingClassifier
import matplotlib.pyplot as plt
import pandas as pd



def Dtree(data,target,new_data,feature_names,target_names):

    testdata = new_data
    pred_tracks = []

    # divide the data set
    x_train, x_test, y_train, y_test = train_test_split(data, target, test_size=0.2, random_state=0)

    # create Decision Tree
    dtc = DecisionTreeClassifier()

    # 使用BaggingClassifier进行集成学习
    bagging = BaggingClassifier(dtc, n_estimators=500, max_samples=0.8)

    # fitting models
    # dtc.fit(x_train, y_train)
    bagging.fit(x_train, y_train)

    # predict
    # train set
    # y_pred = dtc.predict(x_test)
    y_pred = bagging.predict(x_test)

    # accuracy test
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy : ", accuracy)
    # 計算F1-score等指標的報告

    report = classification_report(y_test, y_pred)
    print("classification_report : \n", report)

    # feature importances
    # importances = pd.DataFrame(columns=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
    importances = pd.DataFrame()
    for tree in bagging.estimators_:
        importance = pd.DataFrame(tree.feature_importances_).transpose()
        importances = pd.concat([importances, importance]).reset_index(drop=True)
    means = importances.mean(axis=0)
    mean_dic = {}
    for n,i in enumerate(feature_names.tolist()):
        mean_dic[n] = i
    means = means.rename(mean_dic)
    print(means)

    fig, ax = plt.subplots(figsize=(10, 8))

    ax.barh(range(x_train.shape[1]), means, align='center')
    ax.set_yticks(range(x_train.shape[1]))
    ax.set_yticklabels(feature_names)
    ax.set_xlabel('Importance')
    ax.set_ylabel('Feature')

    plt.subplots_adjust(left=0.3)
    plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/Feature_Importances")

    # fig, ax = plt.subplots()
    # ax.bar(range(x_train.shape[1]), means.tolist(), align='center')
    # ax.set_xticks(range(x_train.shape[1]))
    # ax.set_xticklabels(feature_names)
    # ax.set_xlabel('Feature')
    # ax.set_ylabel('Importance')
    # plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/spotify_chart/Feature_Importances")

    # new set
    for track in testdata:
        new_pred = bagging.predict(track)
        print(new_pred)
        track['pred_type'] = new_pred
        pred_tracks.append(track)

    # print(y_pred)

    # import to new dataset

    result = [pred_tracks,accuracy,bagging]

    return result

    # bagging to chart
    # for i, estimator in enumerate(bagging.estimators_):
    #     print(i)
    #     plt.figure(figsize=(20, 10))
    #     plot_tree(estimator, feature_names=feature_names, filled=True)
    #     plt.title('Tree {}'.format(i))
    #     # plt.show()
    #     plt.savefig("/Users/bensonyang/Desktop/Side-project/Python/SL_spotify/tree_chart/tree_chart_"+str(i),dpi=1028)


    # # 將Decision Tree轉換為Graphviz格式
    # dot_data = export_graphviz(dtc, out_file=None,
    #                          feature_names=feature_names,
    #                          class_names=target_names,
    #                          filled=True, rounded=True,
    #                          special_characters=True)
    # graph = graphviz.Source(dot_data)
    #
    # # 顯示Decision Tree
    # graph.view()


def nn():
    # 生成一個二元分類數據集
    X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)

    # 將數據集切分為訓練集和測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # 建立 MLP 模型
    clf = MLPClassifier(hidden_layer_sizes=(5,), random_state=42)

    # 在訓練集上訓練模型
    clf.fit(X_train, y_train)

    # 在測試集上進行預測
    y_pred = clf.predict(X_test)

    # 計算模型的準確率
    accuracy = clf.score(X_test, y_test)
    print("Accuracy:", accuracy)