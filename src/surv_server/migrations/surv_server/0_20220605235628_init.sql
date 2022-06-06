-- upgrade --
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "telegramchat" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "telegram_name" VARCHAR(255) NOT NULL UNIQUE,
    "enabled" BOOL NOT NULL  DEFAULT False,
    "send_each_photo" BOOL NOT NULL  DEFAULT False
);
CREATE TABLE IF NOT EXISTS "tenant" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(128) NOT NULL UNIQUE,
    "title" VARCHAR(1024)
);
CREATE TABLE IF NOT EXISTS "ftpuser" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(256) NOT NULL,
    "login_hash" VARCHAR(256) NOT NULL UNIQUE,
    "password_hash" VARCHAR(256) NOT NULL,
    "tenant_id" INT NOT NULL REFERENCES "tenant" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_ftpuser_tenant__a91d86" UNIQUE ("tenant_id", "code")
);
CREATE TABLE IF NOT EXISTS "photorecord" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token" VARCHAR(1024)  UNIQUE,
    "datetime" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "fn" VARCHAR(1024) NOT NULL,
    "ftp_user_id" INT REFERENCES "ftpuser" ("id") ON DELETE CASCADE
);
