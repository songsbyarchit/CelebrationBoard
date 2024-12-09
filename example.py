@app.route('/admin/manage', methods=['GET'])
@login_required
def admin_manage():
    if not current_user.is_admin and current_user.email != os.environ.get('SUPER_ADMIN_EMAIL'):
        flash('Access denied')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('admin_manage.html', users=users)

