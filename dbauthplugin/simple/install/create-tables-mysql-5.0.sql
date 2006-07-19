CREATE TABLE `trac_cookies` (
  `envname` varchar(40) NOT NULL,
  `cookie` varchar(40) NOT NULL,
  `username` varchar(40) NOT NULL,
  `ipnr` varchar(15) NOT NULL,
  `unixtime` int(11) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `trac_permissions` (
  `envname` varchar(40) NOT NULL,
  `username` varchar(40) NOT NULL,
  `groupname` varchar(40) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `trac_users` (
  `envname` varchar(40) NOT NULL,
  `username` varchar(40) NOT NULL,
  `password` varchar(40) NOT NULL,
  `email` varchar(100) default NULL,
  UNIQUE KEY `envname` (`envname`,`username`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
