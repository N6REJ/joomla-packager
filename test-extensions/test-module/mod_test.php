<?php
/**
 * @package     Joomla.Site
 * @subpackage  mod_test
 *
 * @copyright   Copyright (C) 2024 Test Company
 * @license     GNU General Public License version 2 or later
 * @version     1.0.0
 */

defined('_JEXEC') or die;

use Joomla\CMS\Helper\ModuleHelper;

require_once dirname(__FILE__) . '/helper.php';

$helper = new ModTestHelper($params);
$items = $helper->getItems();

require ModuleHelper::getLayoutPath('mod_test', $params->get('layout', 'default'));
