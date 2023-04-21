from sklearn import datasets
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from sklearn.datasets import make_classification
from sklearn.tree import export_graphviz
import graphviz


# 生成一個二元分類數據集
X, y = make_classification(n_samples=1000, n_features=10, n_classes=2, random_state=42)

# 將數據集切分為訓練集和測試集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 建立 MLP 模型
clf = MLPClassifier(hidden_layer_sizes=(5,), random_state=42, max_iter=10000)

# 在訓練集上訓練模型
clf.fit(X_train, y_train)

# 在測試集上進行預測
y_pred = clf.predict(X_test)

# 計算模型的準確率
accuracy = clf.score(X_test, y_test)
print("Accuracy:", accuracy)

# 將 MLP 分類器轉換成 Graphviz 的格式
dot_data = export_graphviz(clf, out_file=None,
                           filled=True, rounded=True,
                           special_characters=True)
# 產生類神經圖
graph = graphviz.Source(dot_data)
graph.render("MLPClassifier") # 會產生一個名為 MLPClassifier.pdf 的檔案