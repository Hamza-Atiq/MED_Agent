-- MedAgent Seed Data
-- Run AFTER schema.sql in Supabase SQL Editor

INSERT INTO doctors (name, specialty, phone, whatsapp_id, city, rating) VALUES
('Dr. Ahmed Khan',    'cardiology',  '+923001111111', '923001111111', 'Lahore',     4.9),
('Dr. Sara Malik',    'cardiology',  '+923002222222', '923002222222', 'Karachi',    4.8),
('Dr. Bilal Hussain', 'trauma',      '+923003333333', '923003333333', 'Lahore',     4.7),
('Dr. Fatima Ali',    'trauma',      '+923004444444', '923004444444', 'Islamabad',  4.9),
('Dr. Usman Sheikh',  'neurology',   '+923005555555', '923005555555', 'Lahore',     4.6),
('Dr. Ayesha Raza',   'neurology',   '+923006666666', '923006666666', 'Karachi',    4.8),
('Dr. Imran Qureshi', 'general',     '+923007777777', '923007777777', 'Peshawar',   4.5),
('Dr. Zainab Noor',   'general',     '+923008888888', '923008888888', 'Lahore',     4.7),
('Dr. Hassan Baig',   'cardiology',  '+923009999999', '923009999999', 'Rawalpindi', 4.8),
('Dr. Mariam Iqbal',  'general',     '+923010101010', '923010101010', 'Multan',     4.6)
ON CONFLICT DO NOTHING;
