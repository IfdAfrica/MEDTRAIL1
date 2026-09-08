CREATE TABLE IF NOT EXISTS files (
  id VARCHAR(36) PRIMARY KEY,
  patient_id VARCHAR(100) NOT NULL,
  module VARCHAR(50) NOT NULL,
  document_type VARCHAR(100) NOT NULL,
  original_name VARCHAR(255) NOT NULL,
  stored_name VARCHAR(255) UNIQUE NOT NULL,
  mime_type VARCHAR(150) NOT NULL,
  size INTEGER NOT NULL,
  sha256 VARCHAR(64) NOT NULL,
  uploaded_by VARCHAR(100) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_files_patient ON files(patient_id);
CREATE INDEX IF NOT EXISTS idx_files_module ON files(module);
