-- MedAgent Seed Data — 12 cities × 7 specialties = 84 doctors
-- Run AFTER schema.sql in Supabase SQL Editor
--
-- To start fresh (clears old seed data):
--   DELETE FROM doctors WHERE phone LIKE '+9230%';
-- Then run this file.

INSERT INTO doctors (name, specialty, phone, whatsapp_id, city, rating) VALUES

-- ══════════════════════════════════════════════════════════════
-- LAHORE
-- ══════════════════════════════════════════════════════════════
('Dr. Ahmed Khan',       'cardiology',  '+923011000001', '923011000001', 'Lahore',      4.9),
('Dr. Bilal Hussain',    'trauma',      '+923011000002', '923011000002', 'Lahore',      4.7),
('Dr. Usman Sheikh',     'neurology',   '+923011000003', '923011000003', 'Lahore',      4.6),
('Dr. Zainab Noor',      'general',     '+923011000004', '923011000004', 'Lahore',      4.7),
('Dr. Sadia Qureshi',    'respiratory', '+923011000005', '923011000005', 'Lahore',      4.8),
('Dr. Amna Riaz',        'gynae',       '+923011000006', '923011000006', 'Lahore',      4.9),
('Dr. Kamran Ashraf',    'pediatric',   '+923011000007', '923011000007', 'Lahore',      4.6),

-- ══════════════════════════════════════════════════════════════
-- KARACHI
-- ══════════════════════════════════════════════════════════════
('Dr. Sara Malik',       'cardiology',  '+923022000001', '923022000001', 'Karachi',     4.8),
('Dr. Omar Farooq',      'trauma',      '+923022000002', '923022000002', 'Karachi',     4.7),
('Dr. Ayesha Raza',      'neurology',   '+923022000003', '923022000003', 'Karachi',     4.8),
('Dr. Nadia Siddiqui',   'general',     '+923022000004', '923022000004', 'Karachi',     4.9),
('Dr. Faisal Hashmi',    'respiratory', '+923022000005', '923022000005', 'Karachi',     4.7),
('Dr. Huma Nasir',       'gynae',       '+923022000006', '923022000006', 'Karachi',     4.8),
('Dr. Ali Qasim',        'pediatric',   '+923022000007', '923022000007', 'Karachi',     4.6),

-- ══════════════════════════════════════════════════════════════
-- ISLAMABAD
-- ══════════════════════════════════════════════════════════════
('Dr. Fatima Ali',       'cardiology',  '+923033000001', '923033000001', 'Islamabad',   4.9),
('Dr. Kashif Malik',     'trauma',      '+923033000002', '923033000002', 'Islamabad',   4.7),
('Dr. Rabia Qadir',      'neurology',   '+923033000003', '923033000003', 'Islamabad',   4.8),
('Dr. Tariq Mehmood',    'general',     '+923033000004', '923033000004', 'Islamabad',   4.6),
('Dr. Sana Imran',       'respiratory', '+923033000005', '923033000005', 'Islamabad',   4.7),
('Dr. Lubna Zahid',      'gynae',       '+923033000006', '923033000006', 'Islamabad',   4.9),
('Dr. Hassan Butt',      'pediatric',   '+923033000007', '923033000007', 'Islamabad',   4.8),

-- ══════════════════════════════════════════════════════════════
-- RAWALPINDI
-- ══════════════════════════════════════════════════════════════
('Dr. Hassan Baig',      'cardiology',  '+923044000001', '923044000001', 'Rawalpindi',  4.8),
('Dr. Sana Mirza',       'trauma',      '+923044000002', '923044000002', 'Rawalpindi',  4.7),
('Dr. Nauman Akhtar',    'neurology',   '+923044000003', '923044000003', 'Rawalpindi',  4.6),
('Dr. Maria Khalid',     'general',     '+923044000004', '923044000004', 'Rawalpindi',  4.7),
('Dr. Waqar Ahmed',      'respiratory', '+923044000005', '923044000005', 'Rawalpindi',  4.8),
('Dr. Asma Rehman',      'gynae',       '+923044000006', '923044000006', 'Rawalpindi',  4.9),
('Dr. Junaid Khan',      'pediatric',   '+923044000007', '923044000007', 'Rawalpindi',  4.5),

-- ══════════════════════════════════════════════════════════════
-- PESHAWAR
-- ══════════════════════════════════════════════════════════════
('Dr. Imran Qureshi',    'cardiology',  '+923055000001', '923055000001', 'Peshawar',    4.7),
('Dr. Faisal Yousuf',    'trauma',      '+923055000002', '923055000002', 'Peshawar',    4.6),
('Dr. Sadia Afridi',     'neurology',   '+923055000003', '923055000003', 'Peshawar',    4.7),
('Dr. Asad Khan',        'general',     '+923055000004', '923055000004', 'Peshawar',    4.5),
('Dr. Nadia Gul',        'respiratory', '+923055000005', '923055000005', 'Peshawar',    4.6),
('Dr. Zara Wazir',       'gynae',       '+923055000006', '923055000006', 'Peshawar',    4.8),
('Dr. Bilal Jan',        'pediatric',   '+923055000007', '923055000007', 'Peshawar',    4.5),

-- ══════════════════════════════════════════════════════════════
-- MULTAN
-- ══════════════════════════════════════════════════════════════
('Dr. Mariam Iqbal',     'cardiology',  '+923066000001', '923066000001', 'Multan',      4.7),
('Dr. Rizwan Baig',      'trauma',      '+923066000002', '923066000002', 'Multan',      4.6),
('Dr. Shazia Malik',     'neurology',   '+923066000003', '923066000003', 'Multan',      4.7),
('Dr. Waseem Akram',     'general',     '+923066000004', '923066000004', 'Multan',      4.6),
('Dr. Noor Fatima',      'respiratory', '+923066000005', '923066000005', 'Multan',      4.8),
('Dr. Hina Gillani',     'gynae',       '+923066000006', '923066000006', 'Multan',      4.9),
('Dr. Saad Mehmood',     'pediatric',   '+923066000007', '923066000007', 'Multan',      4.5),

-- ══════════════════════════════════════════════════════════════
-- FAISALABAD
-- ══════════════════════════════════════════════════════════════
('Dr. Adnan Butt',       'cardiology',  '+923077000001', '923077000001', 'Faisalabad',  4.7),
('Dr. Tariq Dar',        'trauma',      '+923077000002', '923077000002', 'Faisalabad',  4.6),
('Dr. Saba Nawaz',       'neurology',   '+923077000003', '923077000003', 'Faisalabad',  4.7),
('Dr. Hina Yousaf',      'general',     '+923077000004', '923077000004', 'Faisalabad',  4.6),
('Dr. Mohsin Ali',       'respiratory', '+923077000005', '923077000005', 'Faisalabad',  4.5),
('Dr. Rubab Ijaz',       'gynae',       '+923077000006', '923077000006', 'Faisalabad',  4.8),
('Dr. Aamir Raza',       'pediatric',   '+923077000007', '923077000007', 'Faisalabad',  4.6),

-- ══════════════════════════════════════════════════════════════
-- QUETTA
-- ══════════════════════════════════════════════════════════════
('Dr. Aziz Kakar',       'cardiology',  '+923088000001', '923088000001', 'Quetta',      4.7),
('Dr. Sadaf Mengal',     'trauma',      '+923088000002', '923088000002', 'Quetta',      4.6),
('Dr. Hamid Baloch',     'neurology',   '+923088000003', '923088000003', 'Quetta',      4.5),
('Dr. Nargis Raisani',   'general',     '+923088000004', '923088000004', 'Quetta',      4.7),
('Dr. Wahab Lehri',      'respiratory', '+923088000005', '923088000005', 'Quetta',      4.6),
('Dr. Farida Zehri',     'gynae',       '+923088000006', '923088000006', 'Quetta',      4.8),
('Dr. Khalid Marri',     'pediatric',   '+923088000007', '923088000007', 'Quetta',      4.5),

-- ══════════════════════════════════════════════════════════════
-- HYDERABAD
-- ══════════════════════════════════════════════════════════════
('Dr. Ramzan Memon',     'cardiology',  '+923099000001', '923099000001', 'Hyderabad',   4.7),
('Dr. Saima Soomro',     'trauma',      '+923099000002', '923099000002', 'Hyderabad',   4.6),
('Dr. Zubair Jamali',    'neurology',   '+923099000003', '923099000003', 'Hyderabad',   4.6),
('Dr. Faryal Talpur',    'general',     '+923099000004', '923099000004', 'Hyderabad',   4.8),
('Dr. Naseem Shaikh',    'respiratory', '+923099000005', '923099000005', 'Hyderabad',   4.5),
('Dr. Bushra Qazi',      'gynae',       '+923099000006', '923099000006', 'Hyderabad',   4.7),
('Dr. Ishaq Panhwar',    'pediatric',   '+923099000007', '923099000007', 'Hyderabad',   4.5),

-- ══════════════════════════════════════════════════════════════
-- SIALKOT
-- ══════════════════════════════════════════════════════════════
('Dr. Amjad Cheema',     'cardiology',  '+923110000001', '923110000001', 'Sialkot',     4.8),
('Dr. Nosheen Gondal',   'trauma',      '+923110000002', '923110000002', 'Sialkot',     4.6),
('Dr. Tahir Rana',       'neurology',   '+923110000003', '923110000003', 'Sialkot',     4.7),
('Dr. Shahida Akhtar',   'general',     '+923110000004', '923110000004', 'Sialkot',     4.6),
('Dr. Nadeem Chaudhry',  'respiratory', '+923110000005', '923110000005', 'Sialkot',     4.7),
('Dr. Farah Bajwa',      'gynae',       '+923110000006', '923110000006', 'Sialkot',     4.9),
('Dr. Umer Shahzad',     'pediatric',   '+923110000007', '923110000007', 'Sialkot',     4.5),

-- ══════════════════════════════════════════════════════════════
-- GUJRANWALA
-- ══════════════════════════════════════════════════════════════
('Dr. Saghir Hussain',   'cardiology',  '+923121000001', '923121000001', 'Gujranwala',  4.7),
('Dr. Tehmina Shakil',   'trauma',      '+923121000002', '923121000002', 'Gujranwala',  4.6),
('Dr. Naveed Gill',      'neurology',   '+923121000003', '923121000003', 'Gujranwala',  4.5),
('Dr. Rukhsana Arshad',  'general',     '+923121000004', '923121000004', 'Gujranwala',  4.7),
('Dr. Kamran Sheikh',    'respiratory', '+923121000005', '923121000005', 'Gujranwala',  4.6),
('Dr. Nasim Chaudhry',   'gynae',       '+923121000006', '923121000006', 'Gujranwala',  4.8),
('Dr. Shahbaz Virk',     'pediatric',   '+923121000007', '923121000007', 'Gujranwala',  4.5),

-- ══════════════════════════════════════════════════════════════
-- BAHAWALPUR
-- ══════════════════════════════════════════════════════════════
('Dr. Riaz Abbasi',      'cardiology',  '+923132000001', '923132000001', 'Bahawalpur',  4.6),
('Dr. Yasmeen Qureshi',  'trauma',      '+923132000002', '923132000002', 'Bahawalpur',  4.5),
('Dr. Shahid Chishti',   'neurology',   '+923132000003', '923132000003', 'Bahawalpur',  4.6),
('Dr. Mehwish Nawaz',    'general',     '+923132000004', '923132000004', 'Bahawalpur',  4.7),
('Dr. Umar Dasti',       'respiratory', '+923132000005', '923132000005', 'Bahawalpur',  4.5),
('Dr. Samia Gillani',    'gynae',       '+923132000006', '923132000006', 'Bahawalpur',  4.8),
('Dr. Asif Khatri',      'pediatric',   '+923132000007', '923132000007', 'Bahawalpur',  4.5)

ON CONFLICT DO NOTHING;
