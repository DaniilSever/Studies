class LinkedList:
    """
    Класс для обработки односвязного списка

    Методы
    ------
    add_element(self, element) -> True:
        Создает список, если его не существует
        Добавляет элементы в конец списка
    remove_head(self) -> True:
        Удаляет элемент списка с головы
    remove_tail(self) -> True:
        Удаляет элемент списка с конца
    reverse_list(self, tail=None, end='\n') -> list:
        Разворачивает список
    clean_list(self) -> list:
        Очищает список
    show_list(self, end="\n") -> list:
        Демонстрирует список

    Атрибуты
    --------
    head - Голова списка, указатель типа данных списка
    """

    def __init__(self, element=None) -> None:
        self.head = element

    class Nodes:
        """
        Класс для создания узлов односвязного списка

        Атрибуты
        --------
        element - Некий элемент узла
        next_node - Ссылка на следующий узел

        """

        def __init__(self, element, next_node=None):
            self.element = element
            self.next_node = next_node

    def add_element(self, element) -> True:
        """
        Создание списка, если его не существует;
        Добавление элемента в конец списка
        """
        if not self.head:
            self.head = self.Nodes(element)
            return True

        node = self.head
        while node.next_node:
            node = node.next_node
        node.next_node = self.Nodes(element)

        if type(node.next_node.element) is type(self.head.element):
            raise TypeError("Incorrect Type")
        return True

    def remove_head(self) -> True:
        """Удаление элемента с головы"""
        if not self.head:
            return None

        self.head = self.head.next_node

        return True

    def remove_tail(self) -> True:
        """Удаление элемента с конца"""
        if not self.head:
            return None

        node = self.head
        while node.next_node.next_node:
            node = node.next_node

        node.next_node = None
        return True

    def reverse_list(self) -> list:
        """Разворот списка"""
        if not self.head:
            return None

        temp = []
        node = self.head
        while node:
            temp.append(node.element)
            node = node.next_node
        revers_list = temp[::-1]
        self.clean_list()
        for item in revers_list:
            self.add_element(item)
        return revers_list

    def clean_list(self) -> True:
        """Очистка списка"""
        if not self.head:
            return None

        self.head = None
        return True

    def show_list(self, end="\n") -> list:
        """Демонстрация списка"""
        if not self.head:
            return None

        linked_list = []
        node = self.head
        while node:
            linked_list.append(node.element)
            print(node.element, end=" / " if node.next_node else "")
            node = node.next_node
        print(end=end)
        return linked_list
