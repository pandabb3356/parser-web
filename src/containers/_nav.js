export default [
  {
    _name: 'CSidebarNav',
    _children: [
      {
        _name: 'CSidebarNavItem',
        name: 'Dashboard',
        to: '/dashboard',
        icon: 'cil-speedometer',
        badge: {
          color: 'danger',
          text: 'NEW'
        }
      },
      {
        _name: 'CSidebarNavTitle',
        _children: ['Organization']
      },
      {
        _name: 'CSidebarNavDropdown',
        name: 'Org Management',
        icon: 'cil-folder',
        items: [
          {
            name: 'Orgs',
            to: '/org/list'
          },
        ]
      },
      {
        _name: 'CSidebarNavTitle',
        _children: ['Parser']
      },
      {
        _name: 'CSidebarNavItem',
        name: 'Version',
        to: '/version',
        icon: 'cil-folder'
      },
        {
        _name: 'CSidebarNavItem',
        name: 'Toggles',
        to: '/toggle',
        icon: 'cil-folder'
      },
    ]
  }
]