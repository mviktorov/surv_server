-- upgrade --
CREATE TABLE IF NOT EXISTS "photorecord" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "datetime" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fn" VARCHAR(1024) NOT NULL UNIQUE,
    "camera_name" VARCHAR(255) NOT NULL
);;
CREATE TABLE IF NOT EXISTS "telegramchat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "telegram_name" VARCHAR(255) NOT NULL UNIQUE,
    "enabled" BOOL NOT NULL  DEFAULT False,
    "send_each_photo" BOOL NOT NULL  DEFAULT False
);-- downgrade --
DROP TABLE IF EXISTS "photorecord";
DROP TABLE IF EXISTS "telegramchat";
