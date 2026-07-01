from pathlib import Path
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
        base_path = Path(self.root_directory_path)
        base_path.mkdir(parents=True, exist_ok=True)

        models_file = base_path / 'models.txt'
        models_index_file = base_path / 'models_index.txt'

        models_file.touch(exist_ok=True)
        models_index_file.touch(exist_ok=True)

        row_number = 1
        with open(models_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    row_number += 1

        with open(models_file, 'a', encoding='utf-8') as file:
            file.write(f'{model.id};{model.name};{model.brand}\n')

        index_data = []
        with open(models_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, pos = line.split(';')
                    index_data.append((key, int(pos)))

        index_data.append((str(model.id), row_number))
        index_data.sort(key=lambda item: item[0])

        with open(models_index_file, 'w', encoding='utf-8') as file:
            for key, pos in index_data:
                file.write(f'{key};{pos}\n')

        return model
    # Задание 1. Сохранение автомобилей и моделей

    def add_car(self, car: Car) -> Car:
        base_path = Path(self.root_directory_path)
        base_path.mkdir(parents=True, exist_ok=True)

        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'

        cars_file.touch(exist_ok=True)
        cars_index_file.touch(exist_ok=True)

        row_number = 1
        with open(cars_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    row_number += 1

        with open(cars_file, 'a', encoding='utf-8') as file:
            file.write(
                f'{car.vin};{car.model};{car.price};{car.date_start};{car.status}\n')

        index_data = []
        with open(cars_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, pos = line.split(';')
                    index_data.append((key, int(pos)))

        index_data.append((str(car.vin), row_number))
        index_data.sort(key=lambda item: item[0])

        with open(cars_index_file, 'w', encoding='utf-8') as file:
            for key, pos in index_data:
                file.write(f'{key};{pos}\n')

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        raise NotImplementedError

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        raise NotImplementedError

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        raise NotImplementedError

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        raise NotImplementedError

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        raise NotImplementedError

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        raise NotImplementedError
