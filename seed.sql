-- Create tables
CREATE TABLE IF NOT EXISTS kpi_sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_type VARCHAR(50) DEFAULT 'manual',
    url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kpi_metrics (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES kpi_sources(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC NOT NULL,
    unit VARCHAR(30) DEFAULT '',
    period_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_source ON kpi_metrics(source_id);
CREATE INDEX IF NOT EXISTS idx_metrics_date ON kpi_metrics(period_date);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON kpi_metrics(metric_name);

-- Seed sources
INSERT INTO kpi_sources (name, source_type, url) VALUES
  ('Ventas Online', 'etl', 'https://tienda.example.com/api/stats'),
  ('Soporte Técnico', 'manual', NULL),
  ('Marketing Digital', 'etl', 'https://analytics.example.com/export'),
  ('Operaciones', 'manual', NULL),
  ('Recursos Humanos', 'manual', NULL);

-- Seed metrics (sample data for 10 days)
DO $$
DECLARE
  s_ventas INT;
  s_soporte INT;
  s_marketing INT;
  s_ops INT;
  s_rrhh INT;
  d DATE;
BEGIN
  SELECT id INTO s_ventas FROM kpi_sources WHERE name = 'Ventas Online';
  SELECT id INTO s_soporte FROM kpi_sources WHERE name = 'Soporte Técnico';
  SELECT id INTO s_marketing FROM kpi_sources WHERE name = 'Marketing Digital';
  SELECT id INTO s_ops FROM kpi_sources WHERE name = 'Operaciones';
  SELECT id INTO s_rrhh FROM kpi_sources WHERE name = 'Recursos Humanos';

  FOR i IN 0..29 LOOP
    d := CURRENT_DATE - (29 - i);
    -- Ventas
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_ventas, 'Ingresos Diarios', round((random() * 17000 + 8000)::numeric, 2), 'MXN', d),
      (s_ventas, 'Pedidos', round((random() * 65 + 15)::numeric, 0), 'count', d),
      (s_ventas, 'Ticket Promedio', round((random() * 400 + 200)::numeric, 2), 'MXN', d),
      (s_ventas, 'Tasa de Conversión', round((random() * 3.5 + 1.5)::numeric, 2), '%', d);
    -- Soporte
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_soporte, 'Tickets Abiertos', round((random() * 35 + 5)::numeric, 0), 'count', d),
      (s_soporte, 'Tickets Resueltos', round((random() * 30 + 5)::numeric, 0), 'count', d),
      (s_soporte, 'Tiempo Medio de Resolución', round((random() * 7.5 + 0.5)::numeric, 2), 'horas', d),
      (s_soporte, 'Satisfacción del Cliente', round((random() * 38 + 60)::numeric, 1), '%', d);
    -- Marketing
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_marketing, 'Visitantes Únicos', round((random() * 4500 + 500)::numeric, 0), 'count', d),
      (s_marketing, 'Tasa de Rebote', round((random() * 40 + 25)::numeric, 1), '%', d),
      (s_marketing, 'CTR Campañas', round((random() * 7.5 + 1.0)::numeric, 2), '%', d),
      (s_marketing, 'Costo por Adquisición', round((random() * 250 + 50)::numeric, 2), 'MXN', d);
    -- Operaciones
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_ops, 'Uptime del Sistema', round((random() * 4.99 + 95)::numeric, 2), '%', d),
      (s_ops, 'Tiempo de Respuesta API', round((random() * 420 + 80)::numeric, 0), 'ms', d),
      (s_ops, 'Errores 5xx', round((random() * 15)::numeric, 0), 'count', d);
    -- RRHH
    INSERT INTO kpi_metrics (source_id, metric_name, metric_value, unit, period_date) VALUES
      (s_rrhh, 'Empleados Activos', round((random() * 10 + 45)::numeric, 0), 'count', d),
      (s_rrhh, 'Tasa de Rotación', round((random() * 7 + 1)::numeric, 1), '%', d),
      (s_rrhh, 'NPS Empleados', round((random() * 55 + 30)::numeric, 0), 'pts', d);
  END LOOP;
END $$;
