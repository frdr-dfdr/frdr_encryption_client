# FRDR Encryption App

## Sample Database Objects for REST API

```
CREATE TABLE requestitem (
    requestitem_id integer NOT NULL,
    token character varying(48),
    item_id integer,
    bitstream_id integer,
    request_email character varying(64),
    request_name character varying(64),
    request_date timestamp without time zone,
    accept_request boolean,
    decision_date timestamp without time zone,
    key_expires timestamp without time zone,
    request_eperson_id integer,
    access_status character varying(30),
    message character varying(1000),
    vault_user_id character varying(64),
    granted_on_vault boolean,
    depositor_action_expires timestamp without time zone,
    depositor_sign_date timestamp without time zone,
    requester_sign_date timestamp without time zone,
    renew_date timestamp without time zone,
    download_expires timestamp without time zone,
    last_decrypted timestamp without time zone,
    intended_use text
);

CREATE SEQUENCE requestitem_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY requestitem
    ADD CONSTRAINT requestitem_pkey PRIMARY KEY (requestitem_id);
ALTER TABLE ONLY requestitem
    ADD CONSTRAINT requestitem_token_key UNIQUE (token);


```
