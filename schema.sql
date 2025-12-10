DROP TABLE IF EXISTS open_houses;
DROP TABLE IF EXISTS listing_media;
DROP TABLE IF EXISTS saved_listings;
DROP TABLE IF EXISTS listing_agents;
DROP TABLE IF EXISTS listing_properties;
DROP TABLE IF EXISTS saved_search_property_type;

DROP TABLE IF EXISTS agent_agencies;
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS properties;

DROP TABLE IF EXISTS saved_searches;
DROP TABLE IF EXISTS user_roles;

DROP TABLE IF EXISTS agents;  

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS addresses;
DROP TABLE IF EXISTS locations;

DROP TABLE IF EXISTS agencies;


DROP TABLE IF EXISTS open_house_types;
DROP TABLE IF EXISTS media_types;
DROP TABLE IF EXISTS property_types;
DROP TABLE IF EXISTS tenures;
DROP TABLE IF EXISTS listing_status;
DROP TABLE IF EXISTS price_types;




CREATE TABLE property_types (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL
);


INSERT INTO property_types (name) VALUES
('apartment'),
('house'),
('townhouse'),
('vacation_home'),
('farm'),
('plot'),
('other');

CREATE TABLE tenures (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL
);

INSERT INTO tenures (name) VALUES
('bostadsratt'),
('äganderätt'),
('hyresrätt'),
('tomträtt');

CREATE TABLE listing_status (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL
);

INSERT INTO listing_status (name) VALUES
('coming_soon'),
('for_sale'),
('sold'),
('removed');

CREATE TABLE price_types (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(100) NOT NULL
);

INSERT INTO price_types (name) VALUES
('starting_price'),
('accepted_price'),
('bid'),
('final_price');

CREATE TABLE media_types (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(50) NOT NULL
);

INSERT INTO media_types (name) VALUES
('image'),
('floorplan'),
('video');

CREATE TABLE open_house_types (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(50) NOT NULL
);

INSERT INTO open_house_types (name) VALUES
('open'),
('booked'),
('digital');



CREATE TABLE locations (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    street_address  VARCHAR(255) NOT NULL,
    postal_code     VARCHAR(32)  NOT NULL,
    city            VARCHAR(100) NOT NULL,
    municipality    VARCHAR(100),
    county          VARCHAR(100),
    country         VARCHAR(100) NOT NULL,
    latitude        NUMERIC,
    longitude       NUMERIC
);

CREATE TABLE addresses (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    street_address  VARCHAR(255) NOT NULL,
    postal_code     VARCHAR(32)  NOT NULL,
    city            VARCHAR(100) NOT NULL,
    municipality    VARCHAR(100),
    county          VARCHAR(100),
    country         VARCHAR(100) NOT NULL
);


CREATE TABLE users (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    first_name  VARCHAR(100),
    last_name   VARCHAR(100),
    phone       VARCHAR(50),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    address_id  INTEGER REFERENCES addresses(id)
);

CREATE TABLE user_roles (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(20) NOT NULL CHECK (name IN ('buyer','seller','agent','admin')),  
    user_id     INTEGER NOT NULL REFERENCES users(id)
);



CREATE TABLE saved_searches (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    query       VARCHAR(255),
    location    VARCHAR(150),

    price_min   NUMERIC,
    price_max   NUMERIC, 

    rooms_min   NUMERIC, -- NULL = "Any"
    rooms_max   NUMERIC, -- NULL = "Any"

    send_email  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE saved_search_property_type (
    saved_search_id BIGINT NOT NULL REFERENCES saved_searches(id) ON DELETE CASCADE,
    property_type_id SMALLINT NOT NULL REFERENCES property_types(id),
    PRIMARY KEY (saved_search_id, property_type_id)
);

CREATE TABLE agencies (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    org_number  VARCHAR(100),
    phone       VARCHAR(50),
    website     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agents (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id),
    title           VARCHAR(100),
    license_number  VARCHAR(100),
    bio             TEXT,
	created_at  	TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at  	TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE agent_agencies (
    agency_id   INTEGER NOT NULL REFERENCES agencies(id),
    agent_id    INTEGER NOT NULL REFERENCES agents(id),
    PRIMARY KEY (agency_id, agent_id)
);

CREATE TABLE properties (
    id                  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    location_id         INTEGER NOT NULL REFERENCES locations(id),
    property_type_id    INTEGER NOT NULL REFERENCES property_types(id),
    tenure_id           INTEGER NOT NULL REFERENCES tenures(id),
    year_built          INTEGER,
    living_area_sqm     NUMERIC,
    additional_area_sqm NUMERIC,
    plot_area_sqm       NUMERIC,
    rooms               NUMERIC,
    floor               INTEGER,
    monthly_fee         NUMERIC,
    energy_class        VARCHAR(50),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE listings (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    agent_id        INTEGER NOT NULL REFERENCES agents(id),
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    status_id       INTEGER NOT NULL REFERENCES listing_status(id),
    list_price      NUMERIC,
    price_type_id   INTEGER REFERENCES price_types(id),
    published_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    external_ref    TEXT,         
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE listing_properties (
    property_id INTEGER NOT NULL REFERENCES properties(id),
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    PRIMARY KEY (property_id, listing_id)
);

CREATE TABLE listing_agents (
    agent_id    INTEGER NOT NULL REFERENCES agents(id),
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    PRIMARY KEY (agent_id, listing_id)
);

CREATE TABLE saved_listings (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, listing_id)
);


CREATE TABLE listing_media (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listing_id      INTEGER NOT NULL REFERENCES listings(id),
    media_type_id   INTEGER NOT NULL REFERENCES media_types(id),
    url             TEXT NOT NULL,
    caption         TEXT,
    position        INTEGER,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE open_houses (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listing_id  INTEGER NOT NULL REFERENCES listings(id),
    starts_at   TIMESTAMPTZ NOT NULL,
    ends_at     TIMESTAMPTZ,
    type_id     INTEGER NOT NULL REFERENCES open_house_types(id),
    note        TEXT
);

CREATE INDEX idx_properties_location    ON properties(location_id);
CREATE INDEX idx_listings_status        ON listings(status_id);
CREATE INDEX idx_listings_agent         ON listings(agent_id);
CREATE INDEX idx_saved_listings_user    ON saved_listings(user_id);
CREATE INDEX idx_saved_searches_user    ON saved_searches(user_id);
CREATE INDEX idx_listing_media_listing  ON listing_media(listing_id);
CREATE INDEX idx_open_houses_listing    ON open_houses(listing_id);
