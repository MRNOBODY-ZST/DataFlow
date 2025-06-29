r'''
1、这段代码是对数据库中影像元数据表 images_metadata 进行增删改查（CRUD）操作的函数封装，
2、基于 SQLAlchemy ORM 的核心 Session，对象进行数据库会话管理和事务控制
3、通过条件构造保证操作定位到指定 image_id 的记录。
4、操作完成后都要调用 db.commit() 提交事务，保证数据写入生效。
'''
from sqlalchemy.orm import Session
from core.models import images_metadata

# 功能：往数据库中插入一条新的影像元数据记录。
def create_metadata(db: Session, metadata):
    db.execute(images_metadata.insert().values(
        image_id=metadata.image_id,
        file_name=metadata.file_name,
        file_path=metadata.file_path,
        resolution=metadata.resolution,
        date=metadata.date,
        batch_id=metadata.batch_id
    ))
    db.commit()

# 功能：根据 image_id 查询数据库中影像元数据记录。
def get_metadata(db: Session, image_id: str):
    return db.execute(images_metadata.select().where(images_metadata.c.image_id == image_id)).first()

# 功能：根据 image_id 更新数据库中影像元数据记录。
def update_metadata(db: Session, image_id: str, resolution=None, date=None):
    update_values = {}
    if resolution is not None:
        update_values['resolution'] = resolution
    if date is not None:
        update_values['date'] = date
    if update_values:
        db.execute(
            images_metadata.update()
            .where(images_metadata.c.image_id == image_id)
            .values(**update_values)
        )
        db.commit()

# 功能：根据 image_id 删除数据库中影像元数据记录。
def delete_metadata(db: Session, image_id: str):
    db.execute(images_metadata.delete().where(images_metadata.c.image_id == image_id))
    db.commit()



# 插入数据
def insert_data(db: Session, data: dict):
    new_data = images_metadata(**data)
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return new_data

# 更新数据
def update_data(db: Session, image_id: str, data: dict):
    db.execute(
        images_metadata.update().where(images_metadata.c.image_id == image_id).values(**data)
    )
    db.commit()

# 删除数据
def delete_data(db: Session, image_id: str):
    db.execute(
        images_metadata.delete().where(images_metadata.c.image_id == image_id)
    )
    db.commit()

# 查询数据
def query_data(db: Session, image_id: str):
    return db.execute(
        images_metadata.select().where(images_metadata.c.image_id == image_id)
    ).first()