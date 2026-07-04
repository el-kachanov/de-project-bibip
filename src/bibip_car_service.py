
from pathlib import Path
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    MODELS_FILE_NAME = 'models.txt'
    MODELS_INDEX_FILE_NAME = 'models_index.txt'
    CARS_FILE_NAME = 'cars.txt'
    CARS_INDEX_FILE_NAME = 'cars_index.txt'
    SALES_FILE_NAME = 'sales.txt'
    SALES_INDEX_FILE_NAME = 'sales_index.txt'

    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        self.models_index: list[tuple[str, int]] | None = None
        self.cars_index: list[tuple[str, int]] | None = None
        self.sales_index: list[tuple[str, int]] | None = None

    def _get_base_path(self) -> Path:
        base_path = Path(self.root_directory_path)
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    def _load_index(self, index_file: Path) -> list[tuple[str, int]]:
        index_data: list[tuple[str, int]] = []
        index_file.touch(exist_ok=True)

        with open(index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                index_key_str, row_pos_str = line.split(';')
                index_data.append((index_key_str, int(row_pos_str)))

        return index_data

    def _save_index(
        self,
        index_file: Path,
        index_data: list[tuple[str, int]],
    ) -> None:
        with open(index_file, 'w', encoding='utf-8') as file:
            for index_key_str, row_pos_int in index_data:
                file.write(f'{index_key_str};{row_pos_int}\n')

    def _get_models_index(self) -> list[tuple[str, int]]:
        if self.models_index is None:
            base_path = self._get_base_path()
            index_file = base_path / self.MODELS_INDEX_FILE_NAME
            self.models_index = self._load_index(index_file)
        return self.models_index

    def _get_cars_index(self) -> list[tuple[str, int]]:
        if self.cars_index is None:
            base_path = self._get_base_path()
            index_file = base_path / self.CARS_INDEX_FILE_NAME
            self.cars_index = self._load_index(index_file)
        return self.cars_index

    def add_model(self, model: Model) -> Model:
        base_path = self._get_base_path()
        models_file = base_path / self.MODELS_FILE_NAME
        models_index_file = base_path / self.MODELS_INDEX_FILE_NAME

        models_file.touch(exist_ok=True)
        models_index = self._get_models_index()

        row_number = len(models_index) + 1

        with open(models_file, 'a', encoding='utf-8') as file:
            file.write(f'{model.id};{model.name};{model.brand}\n')

        models_index.append((str(model.id), row_number))
        models_index.sort(key=lambda item: item[0])
        self._save_index(models_index_file, models_index)

        return model

    def add_car(self, car: Car) -> Car:
        base_path = self._get_base_path()
        cars_file = base_path / self.CARS_FILE_NAME
        cars_index_file = base_path / self.CARS_INDEX_FILE_NAME

        cars_file.touch(exist_ok=True)
        cars_index = self._get_cars_index()

        row_number = len(cars_index) + 1

        with open(cars_file, 'a', encoding='utf-8') as file:
            file.write(
                f'{car.vin};{car.model};{car.price};'
                f'{car.date_start};{car.status.value}\n'
            )

        cars_index.append((car.vin, row_number))
        cars_index.sort(key=lambda item: item[0])
        self._save_index(cars_index_file, cars_index)

        return car
    # Задание 2. Сохранение продаж.

    def sell_car(self, sale: Sale) -> Car:
        from datetime import datetime
        from decimal import Decimal

        base_path = Path(self.root_directory_path)
        base_path.mkdir(parents=True, exist_ok=True)

        sales_file = base_path / 'sales.txt'
        sales_index_file = base_path / 'sales_index.txt'
        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'

        sales_file.touch(exist_ok=True)
        sales_index_file.touch(exist_ok=True)
        cars_file.touch(exist_ok=True)
        cars_index_file.touch(exist_ok=True)

        sales_row_number = 1
        with open(sales_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    sales_row_number += 1

        with open(sales_file, 'a', encoding='utf-8') as file:
            file.write(
                f'{sale.sales_number};{sale.car_vin};'
                f'{sale.cost};{sale.sales_date}\n'
            )

        sales_index_data: list[tuple[str, int]] = []
        with open(sales_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, pos = line.split(';')
                    sales_index_data.append((key, int(pos)))

        sales_index_data.append((sale.sales_number, sales_row_number))
        sales_index_data.sort(key=lambda item: item[0])

        with open(sales_index_file, 'w', encoding='utf-8') as file:
            for key, pos in sales_index_data:
                file.write(f'{key};{pos}\n')

        car_row_number: int | None = None
        with open(cars_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, pos = line.split(';')
                    if key == sale.car_vin:
                        car_row_number = int(pos)
                        break

        if car_row_number is None:
            raise ValueError('Car not found')

        with open(cars_file, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        vin_str, model_str, price_str, date_start_str, _old_status = (
            car_lines[car_row_number - 1].strip().split(';')
        )

        sold_status_str = CarStatus.sold.value
        car_lines[car_row_number - 1] = (
            f'{vin_str};{model_str};{price_str};'
            f'{date_start_str};{sold_status_str}\n'
        )

        with open(cars_file, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        model_id = int(model_str)
        price_value = Decimal(price_str)
        date_start_value = datetime.fromisoformat(date_start_str)

        return Car(
            vin=vin_str,
            model=model_id,
            price=price_value,
            date_start=date_start_value,
            status=CarStatus.sold,
        )
    # Задание 3. Доступные к продаже

    def get_cars(self, status: CarStatus) -> list[Car]:
        from datetime import datetime
        from decimal import Decimal

        base_path = Path(self.root_directory_path)
        cars_file = base_path / 'cars.txt'

        if not cars_file.exists():
            return []

        result: list[Car] = []

        with open(cars_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                vin_str, model_str, price_str, date_start_str, status_str = (
                    line.split(';')
                )

                if status_str != status.value:
                    continue

                model_id = int(model_str)
                price_value = Decimal(price_str)
                date_start_value = datetime.fromisoformat(date_start_str)

                result.append(
                    Car(
                        vin=vin_str,
                        model=model_id,
                        price=price_value,
                        date_start=date_start_value,
                        status=CarStatus(status_str),
                    )
                )

        return result
    # Задание 4. Детальная информация

    def get_car_info(self, vin: str) -> CarFullInfo | None:
        from datetime import datetime
        from decimal import Decimal

        base_path = Path(self.root_directory_path)

        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'
        models_file = base_path / 'models.txt'
        models_index_file = base_path / 'models_index.txt'
        sales_file = base_path / 'sales.txt'

        if not cars_file.exists() or not cars_index_file.exists():
            return None

        car_row_number: int | None = None
        with open(cars_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                key, pos = line.split(';')
                if key == vin:
                    car_row_number = int(pos)
                    break

        if car_row_number is None:
            return None

        with open(cars_file, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        vin_str, model_str, price_str, date_start_str, status_str = (
            car_lines[car_row_number - 1].strip().split(';')
        )

        model_row_number: int | None = None
        with open(models_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                key, pos = line.split(';')
                if key == model_str:
                    model_row_number = int(pos)
                    break

        if model_row_number is None:
            return None

        with open(models_file, 'r', encoding='utf-8') as file:
            model_lines = file.readlines()

        _model_id_str, model_name_str, model_brand_str = (
            model_lines[model_row_number - 1].strip().split(';')
        )

        sales_date_value = None
        sales_cost_value = None

        if status_str == CarStatus.sold.value and sales_file.exists():
            with open(sales_file, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue

                    _sales_number, car_vin_str, cost_str, sales_date_str = (
                        line.split(';')
                    )

                    if car_vin_str == vin_str:
                        sales_date_value = datetime.fromisoformat(
                            sales_date_str
                        )
                        sales_cost_value = Decimal(cost_str)
                        break

        return CarFullInfo(
            vin=vin_str,
            car_model_name=model_name_str,
            car_model_brand=model_brand_str,
            price=Decimal(price_str),
            date_start=datetime.fromisoformat(date_start_str),
            status=CarStatus(status_str),
            sales_date=sales_date_value,
            sales_cost=sales_cost_value,
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        from datetime import datetime
        from decimal import Decimal

        base_path = Path(self.root_directory_path)
        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'

        if not cars_file.exists() or not cars_index_file.exists():
            raise ValueError('Car not found')

        car_row_number: int | None = None
        with open(cars_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                index_key_str, row_pos_str = line.split(';')
                if index_key_str == vin:
                    car_row_number = int(row_pos_str)
                    break

        if car_row_number is None:
            raise ValueError('Car not found')

        with open(cars_file, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        old_vin_str, model_str, price_str, date_start_str, status_str = (
            car_lines[car_row_number - 1].strip().split(';')
        )

        car_lines[car_row_number - 1] = (
            f'{new_vin};{model_str};{price_str};'
            f'{date_start_str};{status_str}\n'
        )

        with open(cars_file, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        new_index_data: list[tuple[str, int]] = []
        for row_number, line in enumerate(car_lines, start=1):
            line = line.strip()
            if not line:
                continue

            current_vin_str, *_rest = line.split(';')
            new_index_data.append((current_vin_str, row_number))

        new_index_data.sort(key=lambda item: item[0])

        with open(cars_index_file, 'w', encoding='utf-8') as file:
            for index_key_str, row_pos_int in new_index_data:
                file.write(f'{index_key_str};{row_pos_int}\n')

        model_id = int(model_str)
        price_value = Decimal(price_str)
        date_start_value = datetime.fromisoformat(date_start_str)
        status_value = CarStatus(status_str)

        return Car(
            vin=new_vin,
            model=model_id,
            price=price_value,
            date_start=date_start_value,
            status=status_value,
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        from datetime import datetime
        from decimal import Decimal

        base_path = Path(self.root_directory_path)
        sales_file = base_path / 'sales.txt'
        sales_index_file = base_path / 'sales_index.txt'
        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'

        if (
            not sales_file.exists()
            or not sales_index_file.exists()
            or not cars_file.exists()
            or not cars_index_file.exists()
        ):
            raise ValueError('Sale not found')

        sale_car_vin: str | None = None

        with open(sales_file, 'r', encoding='utf-8') as file:
            sales_lines = file.readlines()

        new_sales_lines: list[str] = []
        for line in sales_lines:
            line = line.strip()
            if not line:
                continue

            sale_number_str, car_vin_str, _cost_str, _sales_date_str = (
                line.split(';')
            )

            if sale_number_str == sales_number:
                sale_car_vin = car_vin_str
                continue

            new_sales_lines.append(
                f'{sale_number_str};{car_vin_str};'
                f'{_cost_str};{_sales_date_str}\n'
            )

        if sale_car_vin is None:
            raise ValueError('Sale not found')

        with open(sales_file, 'w', encoding='utf-8') as file:
            file.writelines(new_sales_lines)

        new_sales_index_data: list[tuple[str, int]] = []
        for row_number, line in enumerate(new_sales_lines, start=1):
            line = line.strip()
            if not line:
                continue

            sale_number_str, *_rest = line.split(';')
            new_sales_index_data.append((sale_number_str, row_number))

        new_sales_index_data.sort(key=lambda item: item[0])

        with open(sales_index_file, 'w', encoding='utf-8') as file:
            for index_key_str, row_pos_int in new_sales_index_data:
                file.write(f'{index_key_str};{row_pos_int}\n')

        car_row_number: int | None = None
        with open(cars_index_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                index_key_str, row_pos_str = line.split(';')
                if index_key_str == sale_car_vin:
                    car_row_number = int(row_pos_str)
                    break

        if car_row_number is None:
            raise ValueError('Car not found')

        with open(cars_file, 'r', encoding='utf-8') as file:
            car_lines = file.readlines()

        vin_str, model_str, price_str, date_start_str, _status_str = (
            car_lines[car_row_number - 1].strip().split(';')
        )

        available_status_str = CarStatus.available.value
        car_lines[car_row_number - 1] = (
            f'{vin_str};{model_str};{price_str};'
            f'{date_start_str};{available_status_str}\n'
        )

        with open(cars_file, 'w', encoding='utf-8') as file:
            file.writelines(car_lines)

        model_id = int(model_str)
        price_value = Decimal(price_str)
        date_start_value = datetime.fromisoformat(date_start_str)

        return Car(
            vin=vin_str,
            model=model_id,
            price=price_value,
            date_start=date_start_value,
            status=CarStatus.available,
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        from decimal import Decimal

        base_path = Path(self.root_directory_path)
        sales_file = base_path / 'sales.txt'
        cars_file = base_path / 'cars.txt'
        cars_index_file = base_path / 'cars_index.txt'
        models_file = base_path / 'models.txt'
        models_index_file = base_path / 'models_index.txt'

        if (
            not sales_file.exists()
            or not cars_file.exists()
            or not cars_index_file.exists()
            or not models_file.exists()
            or not models_index_file.exists()
        ):
            return []

        vin_to_model_id: dict[str, int] = {}
        vin_to_price: dict[str, Decimal] = {}

        with open(cars_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                vin_str, model_str, price_str, _date_start_str, _status_str = (
                    line.split(';')
                )
                vin_to_model_id[vin_str] = int(model_str)
                vin_to_price[vin_str] = Decimal(price_str)

        model_sales_count: dict[int, int] = {}
        model_max_price: dict[int, Decimal] = {}

        with open(sales_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                _sale_number_str, car_vin_str, _cost_str, _sales_date_str = (
                    line.split(';')
                )

                if car_vin_str not in vin_to_model_id:
                    continue

                model_id = vin_to_model_id[car_vin_str]
                car_price = vin_to_price[car_vin_str]

                model_sales_count[model_id] = (
                    model_sales_count.get(model_id, 0) + 1
                )

                current_max_price = model_max_price.get(model_id)
                if current_max_price is None or car_price > current_max_price:
                    model_max_price[model_id] = car_price

        sorted_model_ids = sorted(
            model_sales_count.keys(),
            key=lambda model_id: (
                -model_sales_count[model_id],
                -model_max_price[model_id],
            ),
        )

        top_model_ids = sorted_model_ids[:3]

        model_info_by_id: dict[int, tuple[str, str]] = {}
        with open(models_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                model_id_str, model_name_str, brand_str = line.split(';')
                model_info_by_id[int(model_id_str)] = (
                    model_name_str,
                    brand_str,
                )

        result: list[ModelSaleStats] = []
        for model_id in top_model_ids:
            model_name_str, brand_str = model_info_by_id[model_id]
            result.append(
                ModelSaleStats(
                    car_model_name=model_name_str,
                    brand=brand_str,
                    sales_number=model_sales_count[model_id],
                )
            )

        return result
