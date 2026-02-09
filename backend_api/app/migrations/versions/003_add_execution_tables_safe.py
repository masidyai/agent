CREATE OR REPLACE FUNCTION create_execution_tables() RETURNS void AS $$
DECLARE
    exists_execution_table BOOLEAN;
    exists_project_files_table BOOLEAN;
    exists_execution_steps_table BOOLEAN;
    exists_enum_type_execution_status BOOLEAN;
    exists_enum_type_file_status BOOLEAN;
BEGIN
    -- Check if the enum types exist
    SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'execution_status') INTO exists_enum_type_execution_status;
    IF NOT exists_enum_type_execution_status THEN
        EXECUTE 'CREATE TYPE execution_status AS ENUM (''pending'', ''completed'', ''failed'', ''running'');';
    END IF;

    SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'file_status') INTO exists_enum_type_file_status;
    IF NOT exists_enum_type_file_status THEN
        EXECUTE 'CREATE TYPE file_status AS ENUM (''available'', ''not_available'');';
    END IF;

    -- Check if the execution table exists
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'execution') INTO exists_execution_table;
    IF NOT exists_execution_table THEN
        EXECUTE 'CREATE TABLE execution (
            id SERIAL PRIMARY KEY,
            status execution_status,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );';
    END IF;

    -- Check if the project_files table exists
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'project_files') INTO exists_project_files_table;
    IF NOT exists_project_files_table THEN
        EXECUTE 'CREATE TABLE project_files (
            id SERIAL PRIMARY KEY,
            file_name VARCHAR(255),
            status file_status,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );';
    END IF;

    -- Check if the execution_steps table exists
    SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'execution_steps') INTO exists_execution_steps_table;
    IF NOT exists_execution_steps_table THEN
        EXECUTE 'CREATE TABLE execution_steps (
            id SERIAL PRIMARY KEY,
            execution_id INTEGER REFERENCES execution(id),
            step_name VARCHAR(255),
            step_order INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );';
    END IF;
END;
$$ LANGUAGE plpgsql;