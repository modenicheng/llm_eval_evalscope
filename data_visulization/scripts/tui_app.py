#!/usr/bin/env python3
"""
TUI程序，用于浏览和对比六个模型的general_qa评测结果。
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from textual import on
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import Header, Footer, ListView, ListItem, Label, Static, Input, Select
    from textual.binding import Binding
    from textual.reactive import reactive
    from textual.screen import Screen
    from textual.message import Message
    from textual.widget import Widget
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    print("错误：Textual库未安装。请使用以下命令安装：")
    print("pip install textual")
    sys.exit(1)

class DataStore:
    """数据存储类，加载整合后的JSON数据"""
    def __init__(self, json_path: str = "integrated_general_qa.json"):
        self.json_path = json_path
        self.data: Dict[str, Dict] = {}
        self.categories: List[str] = []
        self.samples: List[Tuple[str, int, Dict]] = []  # (category, index, sample_data)
        self.load_data()

    def load_data(self):
        """加载JSON数据"""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"整合数据文件不存在：{self.json_path}")

        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # 构建样本列表
        self.categories = sorted(self.data.keys())
        self.samples = []
        for category in self.categories:
            indices = sorted(self.data[category].keys(), key=lambda x: int(x))
            for index in indices:
                sample = self.data[category][index]
                self.samples.append((category, int(index), sample))

        print(f"加载了 {len(self.categories)} 个类别，{len(self.samples)} 个样本")

    def search_samples(self, query: str) -> List[Tuple[str, int, Dict]]:
        """搜索样本（按输入文本）"""
        query = query.lower()
        results = []
        for category, index, sample in self.samples:
            input_text = sample.get("input", "").lower()
            if query in input_text:
                results.append((category, index, sample))
        return results

    def get_sample(self, category: str, index: int) -> Optional[Dict]:
        """获取指定类别和索引的样本"""
        return self.data.get(category, {}).get(str(index))

class SampleListItem(ListItem):
    """样本列表项"""
    def __init__(self, category: str, index: int, sample: Dict):
        super().__init__()
        self.category = category
        self.index = index
        self.sample = sample
        # 显示简短的输入文本（前50个字符）
        input_text = sample.get("input", "")
        # 移除**User**: 前缀
        if input_text.startswith("**User**: \n"):
            input_text = input_text[len("**User**: \n"):]
        display_text = f"{category} #{index}: {input_text[:50]}..." if len(input_text) > 50 else f"{category} #{index}: {input_text}"
        self.label = Label(display_text)

    def compose(self) -> ComposeResult:
        yield self.label

class SampleList(Widget):
    """样本列表组件"""
    def __init__(self, datastore: DataStore):
        super().__init__()
        self.datastore = datastore
        self.list_view = ListView()
        self.current_filter = ""

    def compose(self) -> ComposeResult:
        yield self.list_view

    def on_mount(self) -> None:
        self.load_samples()

    def load_samples(self, query: str = ""):
        """加载样本到列表"""
        self.list_view.clear()
        if query:
            samples = self.datastore.search_samples(query)
        else:
            samples = self.datastore.samples

        for category, index, sample in samples:
            item = SampleListItem(category, index, sample)
            self.list_view.append(item)

        self.current_filter = query

    def get_selected_sample(self) -> Optional[Tuple[str, int, Dict]]:
        """获取当前选中的样本"""
        if self.list_view.index is not None:
            item = self.list_view.children[self.list_view.index]
            if isinstance(item, SampleListItem):
                return item.category, item.index, item.sample
        return None

class ModelOutputWidget(Widget):
    """单个模型输出组件"""
    def __init__(self, model_name: str, prediction: str, acc: float, explanation: str):
        super().__init__()
        self.model_name = model_name
        self.prediction = prediction
        self.acc = acc
        self.explanation = explanation

    def compose(self) -> ComposeResult:
        # 模型名称和准确率
        header = Label(f"[bold]{self.model_name}[/bold] (acc: {self.acc:.2f})")
        header.styles.border = ("heavy", "white")
        header.styles.padding = (0, 0)

        # 预测文本
        prediction_label = Label(self.prediction)
        prediction_label.styles.height = "auto"
        prediction_label.styles.margin = (0, 1)

        # 解释
        explanation_label = Label(f"Judge: {self.explanation}")
        explanation_label.styles.color = "yellow"
        explanation_label.styles.padding = (0, 1)

        yield header
        yield prediction_label
        yield explanation_label

class DetailView(Widget):
    """样本详情视图"""
    def __init__(self):
        super().__init__()
        self.category_label = Label("", id="category")
        self.index_label = Label("", id="index")
        self.input_label = Label("", id="input")
        self.target_label = Label("", id="target")
        self.models_container = Container(id="models-container")
        self.current_sample = None

    def compose(self) -> ComposeResult:
        yield self.category_label
        yield Label("[bold]用户输入:[/bold]", classes="section-title")
        yield ScrollableContainer(self.input_label, classes="content-box")
        yield Label("[bold]参考答案:[/bold]", classes="section-title")
        yield ScrollableContainer(self.target_label, classes="content-box2")
        yield Label("[bold]模型输出:[/bold]", classes="section-title")
        yield self.models_container

    def update_sample(self, category: str, index: int, sample: Dict):
        """更新显示的样本"""
        self.current_sample = (category, index, sample)
        self.category_label.update(f"类别: {category} | 索引: {index}")

        input_text = sample.get("input", "")
        target_text = sample.get("target", "")

        self.input_label.update(input_text)
        self.target_label.update(target_text.strip())

        # 清除之前的模型输出
        self.models_container.remove_children()

        # 添加每个模型的输出
        models = sample.get("models", {})
        for model_name, model_data in models.items():
            prediction = model_data.get("prediction", "")
            acc = model_data.get("acc", 0.0)
            explanation = model_data.get("explanation", "")

            model_widget = ModelOutputWidget(model_name, prediction, acc, explanation)
            self.models_container.mount(model_widget)

        # 重新布局
        self.models_container.refresh(layout=True)

class SearchBar(Widget):
    """搜索栏"""
    def __init__(self):
        super().__init__()
        self.input = Input(placeholder="搜索用户输入...", id="search-input")

    def compose(self) -> ComposeResult:
        yield Label("搜索:")
        yield self.input

    def on_input_changed(self, event: Input.Changed) -> None:
        """输入变化时触发搜索"""
        self.post_message(self.SearchQueryChanged(event.value))

    class SearchQueryChanged(Message):
        """搜索查询变化消息"""
        def __init__(self, query: str):
            super().__init__()
            self.query = query

class ComparisonTUI(App):
    """主TUI应用"""
    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #left-panel {
        width: 20%;
        border: solid white;
        layout: vertical;
    }

    #right-panel {
        width: 80%;
        border: solid white;
        layout: vertical;
    }

    #search-container {
        height: 3;
        border: solid gray;
        margin: 0 1;
    }

    #sample-list-container {
        height: 100%;
        overflow-y: auto;
        width:40;
    }

    #detail-container {
        height: 100%;
        overflow-y: auto;
    }

    .section-title {
        color: cyan;
        margin-top: 1;
        text-style: bold;
    }

    .content-box {
        border: solid gray;
        padding: 0 1;
        margin: 0 1;
        height: 5;
    }
    .content-box2 {
        border: solid gray;
        padding: 0 1;
        margin: 0 1;
        height: 7;
    }

    #models-container {
        layout: vertical;
        overflow-y: auto;
    }

    ModelOutputWidget {
        border: dashed gray;
        height: auto;
        overflow-x: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "退出"),
        Binding("f", "focus_search", "聚焦搜索"),
        Binding("j", "cursor_down", "向下移动", show=False),
        Binding("k", "cursor_up", "向上移动", show=False),
        Binding("enter", "select_sample", "选择样本"),
    ]

    def __init__(self, json_path: str = "integrated_general_qa.json"):
        super().__init__()
        self.datastore = DataStore(json_path)
        self.sample_list = SampleList(self.datastore)
        self.detail_view = DetailView()
        self.search_bar = SearchBar()
        self.status_bar = Label("就绪", id="status-bar")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Container(
                    self.sample_list,
                    id="sample-list-container"
                ),
                Container(
                    self.detail_view,
                    id="detail-container"
                ),
                id="main-container"
            ),
            self.status_bar,
        )
        yield Footer()

    def on_mount(self) -> None:
        self.set_focus(self.sample_list.list_view)
        self.update_status(f"加载了 {len(self.datastore.samples)} 个样本")

    def update_status(self, message: str):
        """更新状态栏"""
        self.status_bar.update(message)

    @on(SearchBar.SearchQueryChanged)
    def on_search_query_changed(self, event: SearchBar.SearchQueryChanged):
        """处理搜索查询变化"""
        self.sample_list.load_samples(event.query)
        self.update_status(f"搜索: '{event.query}' - 找到 {len(self.sample_list.list_view.children)} 个样本")

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected):
        """列表项被选中时更新详情视图"""
        selected = self.sample_list.get_selected_sample()
        if selected:
            category, index, sample = selected
            self.detail_view.update_sample(category, index, sample)
            self.update_status(f"显示: {category} #{index}")

    def action_focus_search(self):
        """聚焦搜索框"""
        self.set_focus(self.search_bar.input)

    def action_cursor_down(self):
        """向下移动光标"""
        self.sample_list.list_view.action_cursor_down()

    def action_cursor_up(self):
        """向上移动光标"""
        self.sample_list.list_view.action_cursor_up()

    def action_select_sample(self):
        """选择当前样本（触发选中事件）"""
        # ListView的选中事件已经处理
        pass

def main():
    """主函数"""
    json_path = "integrated_general_qa.json"
    if not os.path.exists(json_path):
        print(f"错误：整合数据文件不存在 {json_path}")
        print("请先运行 integrate_general_qa.py 生成整合数据")
        return

    app = ComparisonTUI(json_path)
    app.run()

if __name__ == "__main__":
    main()