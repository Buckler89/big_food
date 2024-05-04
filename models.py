import pymongo
from datetime import datetime
from typing import Any, List, Optional, Union, Self, Dict
from pydantic import BaseModel, ValidationError, model_validator, PrivateAttr, Field
from bson.objectid import ObjectId
from pydantic_mongo import AbstractRepository, PydanticObjectId
from pymongo.collection import Collection
import pandas as pd
from enum import Enum, IntEnum



myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient['food_traceability']
semi_finished_products_collection_name = 'semi_finished_products'
suppliers_collection_name = 'suppliers'
raw_materials_collection_name = 'raw_materials'

supplier_collection = mydb[suppliers_collection_name]
raw_material_collection = mydb[raw_materials_collection_name]
semi_finished_product_collection = mydb[semi_finished_products_collection_name]

class QuantityEnum(str, Enum):
    kg = 'kg'
    l = 'l'
    unit = 'unit'

class B(BaseModel):
    _collection_name: str
    name: str
    # id: Optional[PydanticObjectId | None] = None
    id: Optional[PydanticObjectId] = Field(alias="_id", default=None)

    #     _id: Optional[int | None] = None
#     @property
#     def id(self):
#         return self._id
#     @id.setter
#     def id(self, value):
#         self._id = ObjectId(value)

    def insert(self, update=False) -> str:
        unique_field = getattr(self, self._unique_field_name)
        record = None
        # check name is unique
        try:
            q = self.dict(by_alias=True)
            if q.get('_id') is None:
                del q['_id']
            record = mydb[self._collection_name].find_one(q)
            if record:
                # record['id'] = record['_id']
                # del record['_id']
                raise Warning(f"The {self._unique_field_name}={unique_field} already exists in {self._collection_name} collection as is. Nothing to do.")
            elif mydb[self._collection_name].find_one({self._unique_field_name: unique_field}):
                # update
                if update:
                    q.pop("id", None)
                    q.pop("_id", None)
                    mydb[self._collection_name].update_one({self._unique_field_name: unique_field}, {'$set': q})
                    print(f"{self._collection_name} {unique_field} updated successfully")
                else:
                    raise Exception(f"The {self._unique_field_name}={unique_field} already exists in {self._collection_name} collection. Update not allowed")
            else:
                record = mydb[self._collection_name].insert_one(q)
        except Exception as e:
            print(e)
            record = None
        return record


class Supplier(B):
    _collection_name: str = PrivateAttr(suppliers_collection_name)
    _unique_field_name: str = PrivateAttr('name')

    address: Optional[str | None] = None
    phone: Optional[str | None] = None
    email: Optional[str | None] = None

    @model_validator(mode='after')
    def validate(self, values: Any):
        if len(self.phone) < 8:
            raise ValueError("The phone number must be at least 8 digits")
        if '@' not in self.email:
            raise ValueError("The email must contain the @ symbol")
        return values


class RawMaterial(B):
    _collection_name: str = PrivateAttr(raw_materials_collection_name)
    _unique_field_name: str = PrivateAttr('batch_number')

    date: datetime
    expiration_date: datetime
    batch_number: str
    quantity: float
    consumed_quantity: float = 0
    quantity_unit: QuantityEnum
    is_finished: bool = False

    document_number: str
    supplier_id: PydanticObjectId

    @model_validator(mode='after')
    def validate(self, values: Any):
        if not isinstance(self.date, datetime):
            self.date = datetime.combine(self.date, datetime.min.time())
        if not isinstance(self.expiration_date, datetime):
            self.expiration_date = datetime.combine(self.expiration_date, datetime.min.time())
        if self.date > self.expiration_date:
            raise ValueError("The expiration date cannot be earlier than the production date")
        if self.quantity <= 0:
            raise ValueError("The quantity must be greater than zero")
        if not supplier_collection.find_one({'_id': ObjectId(self.supplier_id)}):
            raise ValueError("The supplier does not exist")
        # check ot exist another raw material with the same fields

        return values


class SemiFinishedProduct(B):
    """
    Semi-finished product A, B or finished product
    """
    _collection_name: str = PrivateAttr(semi_finished_products_collection_name)
    _unique_field_name: str = PrivateAttr('batch_number')

    date: datetime
    expiration_date: datetime
    batch_number: str
    quantity: float
    consumed_quantity: float = 0
    quantity_unit: QuantityEnum
    is_finished: bool = False

    ingredients: Dict[PydanticObjectId, Union[int, float]]  # list of name of RawMaterial or SemiFinishedProduct and relative used quantity

    @model_validator(mode='after')
    def validate(self, values: Any):
        if not isinstance(self.date, datetime):
            self.date = datetime.combine(self.date, datetime.min.time())
        if not isinstance(self.expiration_date, datetime):
            self.expiration_date = datetime.combine(self.expiration_date, datetime.min.time())
        if self.date > self.expiration_date:
            raise ValueError("The expiration date cannot be earlier than the production date")
        if len(self.ingredients) == 0:
            raise ValueError("The product must have at least one ingredient")
        # check if all ingredients exist
        for ingredient in self.ingredients:
            if (not raw_material_collection.find_one({'_id':  ObjectId(ingredient)}) and
                    not semi_finished_product_collection.find_one({'_id':  ObjectId(ingredient)})):
                raise ValueError("The ingredient does not exist")
        return values


def get_supplier_by_id(supplier_id: str) -> Union[Supplier, None]:
    supplier = supplier_collection.find_one({'_id': ObjectId(supplier_id)})
    if supplier:
        return Supplier(**supplier)
    return None


def get_raw_material_by_id(raw_material_id: str) -> Union[RawMaterial, None]:
    raw_material = raw_material_collection.find_one({'_id': ObjectId(raw_material_id)})
    if raw_material:
        return RawMaterial(**raw_material)
    return None

def get_raw_material_by_batch_number(batch_number: str) -> Union[RawMaterial, None]:
    raw_material = raw_material_collection.find_one({'batch_number': batch_number})
    if raw_material:
        return RawMaterial(**raw_material)
    return None

def get_semi_finished_product_by_id(semi_finished_product_id: str) -> Union[SemiFinishedProduct, None]:
    semi_finished_product = semi_finished_product_collection.find_one({'_id': ObjectId(semi_finished_product_id)})
    if semi_finished_product:
        return SemiFinishedProduct(**semi_finished_product)
    return None

def get_semi_finished_product_by_batch_number(batch_number: str) -> Union[SemiFinishedProduct, None]:
    semi_finished_product = semi_finished_product_collection.find_one({'batch_number': batch_number})
    if semi_finished_product:
        return SemiFinishedProduct(**semi_finished_product)
    return None

def get_all_suppliers() -> List[Supplier]:
    return [Supplier(**supplier) for supplier in supplier_collection.find()]


def get_all_raw_materials() -> List[RawMaterial]:
    return [RawMaterial(**raw_material) for raw_material in raw_material_collection.find()]


def get_all_semi_finished_products() -> List[SemiFinishedProduct]:
    return [SemiFinishedProduct(**semi_finished_product) for semi_finished_product in semi_finished_product_collection.find()]


def delete_supplier_by_id(supplier_id: str) -> bool:
    result = supplier_collection.delete_one({'_id': ObjectId(supplier_id)})
    return result.deleted_count > 0


def delete_raw_material_by_id(raw_material_id: str) -> bool:
    result = raw_material_collection.delete_one({'_id': ObjectId(raw_material_id)})
    return result.deleted_count > 0


def delete_semi_finished_product_by_id(semi_finished_product_id: str) -> bool:
    result = semi_finished_product_collection.delete_one({'_id': ObjectId(semi_finished_product_id)})
    return result.deleted_count > 0


def query_collection(constructor, collection, mode='AND', **kwargs) -> List[Union[Supplier, RawMaterial, SemiFinishedProduct]]:

    if mode == 'AND':
        query = {}
    elif mode == 'OR':
        query = []
    for key, value in kwargs.items():
        if key not in constructor.__fields__:
            raise ValueError(f"Invalid field {key}")
        if mode == 'AND':
            if isinstance(value, str):
                query[key] = {"$regex": value, "$options": "i"} # AND format
            else:
                query[key] = value
        elif mode == 'OR':
            if isinstance(value, str):
                query.append({key: {"$regex": value, "$options": "i"}})  # OR format
            else:
                query.append({key: value})
    if mode == 'OR':
        query = {"$or": query} if query else {}
    results = collection.find(query)
    return [constructor(**r) for r in results]
    # results_with_id = list()
    # for r in results:
    #     r['id'] = r['_id']
    #     del r['_id']
    #     results_with_id.append(r)
    # return [constructor(**r) for r in results_with_id]

def to_dataframes(List: List[Union[Supplier, RawMaterial, SemiFinishedProduct]]) -> pd.DataFrame:
    as_dict = [r.dict(by_alias=True) for r in List]
    df = pd.DataFrame(as_dict)
    return df

def to_class(df: pd.DataFrame, constructor) -> List[Union[Supplier, RawMaterial, SemiFinishedProduct]]:
    return [constructor(**r) for r in df.to_dict(orient='records')]


if __name__ == '__main__':
    # USAGE EXAMPLE

    print(f"Collection in mongodb: {myclient.list_database_names()}")
    try:
        for i, supplier_name in enumerate(['Latteria', 'Macelleria', 'Pasticceria']):
            supplier = Supplier(
                name=supplier_name,
                address=f'Via {supplier_name} {i}',
                phone=f'{i}2345678',
                email=f'{supplier_name}@{supplier_name}.it'
            )
            supplier_record = supplier.insert()
    except ValidationError as e:
        print(e.json())

    try:
        raw_material = RawMaterial(
            date=datetime(2021, 3, 1),
            batch_number='A123',
            name='Latte',
            document_number='123',
            supplier_id=supplier_collection.find_one({'name': 'Latteria'})['_id'],
            expiration_date=datetime(2021, 3, 10),
            quantity=10,
            quantity_unit=QuantityEnum.l
        )
        raw_material_record = raw_material.insert()
    except ValidationError as e:
        print(e.json())

    try:
        raw_material = RawMaterial(
            date=datetime(2021, 3, 1),
            batch_number='A124',
            name='Farina',
            document_number='345',
            supplier_id=supplier_collection.find_one({'name': 'Latteria'})['_id'],
            expiration_date=datetime(2021, 3, 10),
            quantity=10,
            quantity_unit=QuantityEnum.kg
        )
        # raw_material_collection.insert_one(raw_material.dict())
        raw_material_record = raw_material.insert()
    except ValidationError as e:
        print(e.json())

    try:
        semi_finished_product = SemiFinishedProduct(
            name='Crema',
            date=datetime(2021, 3, 1),
            expiration_date=datetime(2021, 3, 10),
            ingredients={
                raw_material_collection.find_one({'batch_number': 'A123'})['_id']: 5,
                raw_material_collection.find_one({'batch_number': 'A124'})['_id']: 2
            },
            batch_number='B123',
            quantity=10,
            quantity_unit=QuantityEnum.kg
        )
        # semi_finished_product_collection.insert_one(semi_finished_product.dict())
        semi_finished_product_record = semi_finished_product.insert()

    except ValidationError as e:
        print(e.json())

    suppliers = query_collection(Supplier, supplier_collection, **{"name": "L"})
    raw_materials = query_collection(RawMaterial, raw_material_collection, **{"name": "L"})
    semi_finished_products = query_collection(SemiFinishedProduct, semi_finished_product_collection, **{"name": "C"})
    print()

